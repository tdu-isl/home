#!/bin/python3

from datetime import date
import json
import re


# CONF_TEMPLATE_PATH = ".draft/conf-template.json"
CONF_PATH = ".draft/conf.json"
TEMPLATE_PATH = ".draft/.newstemplate"
TEMPLATE_KEY_PATTERN = "\${(.+?)}"

INSERT_TARGET = "index.html"
INSERT_SORT_KEY_PATTERN = "<dt><span>(.+?)</span></dt>"
INSERT_SORT_KEY_CONVERT = lambda x: date(*map(int, x.split("-")))

MODIFIERS_RAW = {"skip": "SKIP", "error": "ERROR", "message": "MSG", "done": "DONE"}
MODIFIER_MAX_LEN = max(map(len, MODIFIERS_RAW.values()))
MODIFIERS = {
    "skip": f'[ \033[35m{MODIFIERS_RAW["skip"]:^{MODIFIER_MAX_LEN}}\033[39m ]',
    "error": f'[ \033[31m{MODIFIERS_RAW["error"]:^{MODIFIER_MAX_LEN}}\033[39m ]',
    "msg": f'[ \033[36m{MODIFIERS_RAW["message"]:^{MODIFIER_MAX_LEN}}\033[39m ]',
    "done": f'[ \033[32m{MODIFIERS_RAW["done"]:^{MODIFIER_MAX_LEN}}\033[39m ]'
}


def make_news():
    # with open(CONF_TEMPLATE_PATH, mode="r") as f:
    #     data = json.load(f)

    with open(CONF_PATH, mode="r") as f:
        # for key, val in json.load(f).items():
        #     if key not in data:
        #         continue

        #     data[key] = val

        data = json.load(f)

    with open(data["body"], mode="r") as f:
        data["body"] = f.read().replace("\n", "<br>")

    news = []
    with open(TEMPLATE_PATH, mode="r") as f:
        matcher = re.compile(TEMPLATE_KEY_PATTERN)
        news = f.readlines()
        for i, line in enumerate(news):
            for match_key in matcher.finditer(line):
                matched = match_key.group(0)
                key = match_key.group(1)
                if key not in data:
                    print(f'{MODIFIERS["skip"]} {key} is not defined in the {CONF_PATH}')
                    continue

                news[i] = news[i].replace(matched, data[key])

    return "".join(news)


def insert(news):
    with open(INSERT_TARGET, mode="r") as f:
        insert_target = f.readlines()

    matcher = re.compile(INSERT_SORT_KEY_PATTERN)
    news_key = INSERT_SORT_KEY_CONVERT(matcher.search(news).group(1))
    insert_point, done = -1, False
    for i, line in enumerate(insert_target):
        for key in matcher.findall(line):
            key = INSERT_SORT_KEY_CONVERT(key)
            if news_key >= key:
                insert_point = i
                done = True
                break

        if done:
            break

    if insert_point < 0:
        with open("tmp", mode="w") as f:
            f.write(news)

        print(f'{MODIFIERS["error"]} cannot find insert point')
        print(f'{MODIFIERS["error"]} but, output news to \"./tmp\"')
        return

    insert_target.insert(insert_point, news)
    n = news.count("\n")
    with open(INSERT_TARGET, mode="w") as f:
        f.write("".join(insert_target))

    print(f'{MODIFIERS["msg"]} inserted line. {insert_point + 1} - {insert_point + 1 + n - 1}')
    print(f'{MODIFIERS["done"]} terminated successfully')


def main():
    insert(make_news())


if __name__ == "__main__":
    main()
