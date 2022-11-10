import argparse
import logging
import os
import sys

import asn1tools

from os import walk

state = ""
didPt = False
didPl = False
lastKey = ""
lastVal = ""

def espacos(profundidade: int):
    return ".   " * profundidade


def valor_membro(membro):
    if isinstance(membro, (bytes, bytearray)):
        return bytes(membro).hex()
    return membro


def print_list(lista: list, profundidade: int):
    indent = espacos(profundidade)
    for membro in lista:
        if type(membro) is dict:
            print_dict(membro, profundidade + 1)
        # else:
            # print(f"{indent}valor_membro(membro)")


def print_dict(entidade: dict, profundidade: int):
    global lastKey, lastVal, didPl, didPt, state
    indent = espacos(profundidade)
    for key in sorted(entidade):
        # print (key)
        membro = entidade[key]
        if type(membro) is dict:
            # print(f"{indent}{key}:")
            print_dict(membro, profundidade + 1)
        elif type(membro) is list:
            # print(f"{indent}{key}: [")
            print_list(membro, profundidade + 1)
            # print(f"{indent}] <== {key}")
        else:
            if key == "codigoCargo" and f"{valor_membro(membro)}" != "('cargoConstitucional', 'presidente')":
                break
            if key == "municipio":
                print(f"{valor_membro(membro)}", end='')
            if key == "zona" or key == "secao": 
                print(f",{valor_membro(membro)}", end='')
            if key == "codigo":
                lastKey = key
                lastVal = valor_membro(membro)
                if lastVal == 13:
                    didPt = True
                if lastVal == 22:
                    didPl = True
                if lastVal == 22 and not didPt:
                    print(f"candidato_13 = 0")
            if key == "quantidadeVotos" and lastKey == "codigo":
                lastKey = ""
                print(f",{valor_membro(membro)}", end='')


def processa_bu(asn1_paths: list, bu_path: str):
    global lastKey, lastVal, didPl, didPt
    didPt = False
    didPl = False
    lastKey = ""
    lastVal = ""

    conv = asn1tools.compile_files(asn1_paths, codec="ber")
    with open(bu_path, "rb") as file:
        envelope_encoded = bytearray(file.read())
    envelope_decoded = conv.decode("EntidadeEnvelopeGenerico", envelope_encoded)
    bu_encoded = envelope_decoded["conteudo"]
    del envelope_decoded["conteudo"]  # remove o conteúdo para não imprimir como array de bytes
    # print("EntidadeEnvelopeGenerico:")
    # print_dict(envelope_decoded, 1)
    bu_decoded = conv.decode("EntidadeBoletimUrna", bu_encoded)
    # print("EntidadeBoletimUrna:")
    print_dict(bu_decoded, 1)
    if not didPl:
        print(f",0", end='')
    print("")


def main():
    global state
    parser = argparse.ArgumentParser(
        description="Converte um Boletim de Urna (BU) da Urna Eletrônica (UE) e imprime um extrato",
        formatter_class=argparse.RawTextHelpFormatter)

    f = []
    for (dirpath, dirnames, filenames) in walk("./logjez/"):
        f.extend(filenames)
        break
    
    print(f"municipio,zona,secao,candidato_13,candidato_22")

    f.sort()

    for file in f:
        root, ext = os.path.splitext(file)
        if ext == ".bu":
            bu_path = "./logjez/" + file
            asn1_paths = ["./bu.asn1"]

            if not os.path.exists(bu_path):
                logging.error("Arquivo do BU (%s) não encontrado", bu_path)
                sys.exit(-1)
            for asn1_path in asn1_paths:
                if not os.path.exists(asn1_path):
                    logging.error("Arquivo de especificação do BU (%s) não encontrado", asn1_path)
                    sys.exit(-1)

            if os.stat(bu_path).st_size != 0:
                processa_bu(asn1_paths, bu_path)

if __name__ == "__main__":
    main()
