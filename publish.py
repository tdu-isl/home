#!/bin/python3

import json
import re


CONF_TEMPLATE_PATH = ".draft/conf-template.json"
CONF_PATH = ".draft/conf.json"
TEMPLATE_PATH = ".draft/.newstemplate"
TEMPLATE_KEY_PATTERN = "\${(.+?)}"

INSERT_TARGET = "index.html"
INSERT_SORT_KEY_PATTERN = "<dt><span>(.+?)</span></dt>"  # 単純に文字列比較する


def make_news():
    # with open(CONF_TEMPLATE_PATH, mode="r") as f:
    #     data = json.load(f)

    with open(CONF_PATH, mode="r") as f:
        data = json.load(f)
        # for key, val in json.load(f).items():
        #     if key not in data:
        #         continue

        #     data[key] = val

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
                news[i] = news[i].replace(matched, data[key])

    return "".join(news)


def insert(news):
    with open(INSERT_TARGET, mode="r") as f:
        insert_target = f.readlines()

    matcher = re.compile(INSERT_SORT_KEY_PATTERN)
    news_key = matcher.match(news).group(1)
    insert_point, done = -1, False
    for i, line in enumerate(insert_target):
        for key in matcher.findall(line):
            if news_key >= key:
                insert_point = i
                done = True
                break

        if done:
            break

    if insert_point < 0:
        with open("tmp", mode="w") as f:
            f.write(news)

        print("cannot find insert point")
        print("but, output into \"./tmp\"")
        return

    insert_target.insert(insert_point, news)
    with open(INSERT_TARGET, mode="w") as f:
        f.write("".join(insert_target))


def main():
    insert(make_news())


if __name__ == "__main__":
    main()
