<?php

$divider = $argv[1] ?? "";
echo "Using divider $divider\n";

// todos os estados
$states = ['ac','al','am','ap','ba','ce','df','es','go','ma','mg','ms','mt','pa','pb','pe','pi','pr','rj','rn','ro','rr','rs','sc','se','sp','to'];
foreach ($states as $state) {
    if (!is_dir(__DIR__. "/urna/$state/")) {
        mkdir(__DIR__. "/urna/$state/", 0777, true);
    }
	$pathState = __DIR__. "/urna/$state/$state-cs.json";
	if (!file_exists($pathState)) {
		$urlState = "https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/407/config/$state/$state-p000407-cs.json";
		$raw = file_get_contents($urlState);
		file_put_contents($pathState, $raw);
		$jsonState = json_decode($raw, true);
	} else {
		$raw = file_get_contents($pathState);
		$jsonState = json_decode($raw, true);
	}

	foreach ($jsonState["abr"][0]["mu"] as $jsonMu) {
		$codMu = $jsonMu["cd"];

		foreach ($jsonMu["zon"] as $jsonZon) {
			$codZon = $jsonZon["cd"];

			foreach ($jsonZon["sec"] as $jsonSec) {
				$codSec = $jsonSec["ns"];

                if (substr($codSec, -1) != $divider && $divider != "") continue;

				$urnaIndexUrl  = "https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/407/dados/$state";
				$urnaIndexUrl .= "/$codMu/$codZon/$codSec/p000407-$state-m$codMu-z$codZon-s$codSec-aux.json";

				$pathUrnaIndex = __DIR__. "/urna/$state/$state-$codMu-$codZon-$codSec-aux.json";

				if (!file_exists($pathUrnaIndex)) {
					echo "Urna index for $state-$codMu-$codZon-$codSec downloaded!\n";
					$raw = file_get_contents($urnaIndexUrl);
					file_put_contents($pathUrnaIndex, $raw);
					$jsonUrnaIndex = json_decode($raw, true);
				} else {
					echo "Urna index for $state-$codMu-$codZon-$codSec cached!\n";

					$raw = file_get_contents($pathUrnaIndex);
					$jsonUrnaIndex = json_decode($raw, true);
				}

				$buHash = $jsonUrnaIndex["hashes"][0]["hash"];
				$buFile = explode(".", $jsonUrnaIndex["hashes"][0]["nmarq"][0])[0];

				$urnaBuUrl  = "https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/407/dados/$state";
				$urnaBuUrl .= "/$codMu/$codZon/$codSec/$buHash/$buFile.bu";

				$pathUrnaBu = __DIR__. "/urna/$state/$state-$codMu-$codZon-$codSec-$buFile.bu";

				if (!file_exists($pathUrnaBu)) {
					echo "Urna '.bu' for $state-$codMu-$codZon-$codSec downloaded!\n";
					$raw = file_get_contents($urnaBuUrl);
					file_put_contents($pathUrnaBu, $raw);
				}
			}
		}
	}
}
