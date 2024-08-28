import time
from taus import get_taus_qe
import os
import json
import glob
import regex as re
import pandas as pd
from rich import print
# getpass
# from datasets import load_dataset

data = {
    "source": {"value": "This is a test.", "language": "en"},
    "targets": [{"value": "Das ist ein Test.", "language": "de"}],
    "metrics": [{"uid": "taus_qe", "version": "2.0.0"}],
}

source_lang = "en"
# x = get_taus_qe_mockup(data)
supported_locales = ["de"]  # ,"es" "fr", "de"]
aggregate_data = []
# glob_path_pattern = ""

for target_lang in supported_locales:
    for file_path in glob.glob(
        f"files/**/YSC-Strata_Evaluation-Sample_{target_lang}_OMT/mtpe/QE_scores.xlsx",
        recursive=True,
    ):
        # Print the absolute path of each found file
        print(f"====== {file_path} ======")
        partial_data = []
        pattern_engine = r"(?<=output/)\w+(?=/YSC-Strata)"
        match = re.search(pattern_engine, file_path)
        if match:
            engine = match.group()
            print(f"{engine=} / {target_lang=}")  # Outputs: google
        else:
            print("No match found.")

        # pattern_locale = r"(?<=_)\w+(?=_OMT/mtpe)"
        # match = re.search(pattern_locale, file_path)
        # if match:
        #     target_lang = match.group()
        #     print(target_lang)  # Outputs: google
        # else:
        #     print("No match found.")

        # if target_lang not in supported_locales:
        #     continue

        absolute_path = os.path.abspath(file_path)
        # print(absolute_path)

        df = pd.read_excel(absolute_path)

        # rename score column to comet_score
        df.rename(columns={"score": "comet"}, inplace=True)

        # df = add_taus_score_col(df)
        # df["taus_score"] = [7, 8, 9]
        # df["taus_score"] = df.apply(
        #     lambda row: get_taus_qe_mockup(
        #         {
        #             "source": {"value": row["src"], "language": source_lang},
        #             "targets": [{"value": row["mt"], "language": target_lang}],
        #             "metrics": [{"uid": "taus_qe", "version": "2.0.0"}],
        #         }
        #     )["estimates"][0]["metrics"][0]["value"],
        #     axis=1,
        # )

        # df["taus_score"] = get_taus_qe_mockup(data)["estimates"][0]["metrics"][0]["value"]

        bitexts = dict(zip(df.src, df.mt))

        data = [
            {
                "source": {"value": src, "language": source_lang},
                "targets": [{"value": mt, "language": target_lang}],
                "metrics": [{"uid": "taus_qe", "version": "2.0.0"}],
            }
            for src, mt in dict(zip(df.src, df.mt)).items()
        ]

        time.sleep(3)  # Sleep for 3 seconds
        taus_qe_metrics = [get_taus_qe(unit) for unit in data]
        # scores = [
        #     metric["estimates"][0]["metrics"][0]["value"] for metric in taus_qe_metrics
        # ]
        scores = [
            json.loads(metric)["estimates"][0]["metrics"][0]["value"]
            for metric in taus_qe_metrics
        ]

        # print(scores)
        # add column for taus_score
        df["taus"] = scores

        # print(df["taus"])
        # print(df)

        comet = df.comet
        taus = df.taus

        comet_sysem_score = sum(comet.tolist()) / len(comet.tolist())
        taus_sysem_score = sum(taus.tolist()) / len(taus.tolist())

        metrics = [
            {"engine": engine, "comet": comet_sysem_score, "taus_qe": taus_sysem_score}
        ]
        # aggregate_data.append({"locale": target_lang, "metrics": metrics})

        metrics = {
            "locale": target_lang,
            "engine": engine,
            "comet": comet_sysem_score,
            "taus_qe": taus_sysem_score,
        }
        partial_data.append(metrics)
        aggregate_data.append(metrics)

        aggregate_df_part = pd.DataFrame(partial_data)
        aggregate_df_part.to_excel(f"metrics_{target_lang}_{engine}.xlsx", index=False)

        # print(aggregate_data)


aggregate_df = pd.DataFrame(aggregate_data)
aggregate_df.to_excel("aggregate_metrics2.xlsx", index=False)
