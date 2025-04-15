from glob import iglob
import os
import json
import re

TEMPLATE = {
    "Dialogue": [
        "#Person1#: Is there a bus that'll go all the way to Sons from PHS?",
    ],
    "Topic": "bus route",
    "QASumm": "#Person2# tells #Person1# the bus route to get to Sons.",
    "AllTopic": [
        "bus route",
        "wash the dishes",
        "milk-delivery experience",
        "delayed order",
    ],
    "Index": [0],
}
EMPTY_TEMPLATE = {
    "_dact_id_list": [],
    "Dialogue": [],
    "Topic": "",
    "QASumm": "",
    "AllTopic": [],
    "Index": [],
}

DACT_ROOT = "dialogueActs"
ABS_ROOT = "abstractive"
TOPIC_ROOT = "topics"

for filename in iglob("*.json", root_dir=DACT_ROOT):
    # skip if not matching file under other roots
    if not os.path.exists(f"{ABS_ROOT}/{filename}"):
        continue
    if not os.path.exists(f"{TOPIC_ROOT}/{filename}"):
        continue

    out = EMPTY_TEMPLATE.copy()

    with open(f"{DACT_ROOT}/{filename}") as fp:
        dacts = json.load(fp)
        for act in dacts:
            speaker = act["speaker"]
            text = re.sub(r"\ \<\w+\>", "", act["text"])
            text = re.sub(r"\<\w+\>\ ", "", text)
            text = re.sub(r"\<\w+\>", "", text)

            out["Dialogue"].append(f"#{speaker}#: {text}")
            out["_dact_id_list"].append(act["id"])
            out["Index"].append(0)

    with open(f"{TOPIC_ROOT}/{filename}") as fp:
        topics: list[dict] = json.load(fp)

        for each_topic in topics:
            if each_topic not in out["AllTopic"]:
                out["AllTopic"].append(each_topic["topic"])
            topic_id = out["AllTopic"].index(each_topic["topic"])

            for each_dact in each_topic["dialogueacts"]:
                pos_in_dact_list = out["_dact_id_list"].index(each_dact["id"])

                out["Index"][pos_in_dact_list] = topic_id

    with open(f"{ABS_ROOT}/{filename}") as fp:
        abstractive: list[dict] = json.load(fp)
        out["QASumm"] = " ".join(
            each_abs["text"]
            for each_abs in abstractive
            if each_abs["type"] == "abstract"
        )
        out["Topic"] = " ".join(
            each_abs["text"]
            for each_abs in abstractive
            if each_abs["type"] == "problems"
        )

    with open(f"merged/{filename}", "w") as fp:
        json.dump(out, fp)
