import json
import re

with open("txt.txt", "r", encoding="utf-8") as t:
    content = t.read()
    result = [

    ]
    search_razdels = [list(result) for result in re.findall(r'РАЗДЕЛ(.*?)(?=(РАЗДЕЛ|$))', content, re.DOTALL)]
    if not search_razdels:
        json_result = {
            content: [

            ]
        }
        result.append(json_result)
    else:
        for search_razdel in search_razdels:
            json_result = {
                search_razdel[0]: [

                ]
            }
            result.append(json_result)

    for item in result:
        item_key = [*item][0]
        search_glavas = [list(result) for result in re.findall(r'Глава(.*?)(?=(Глава|$))', item_key, re.DOTALL)]
        if not search_glavas:
            json_result = {
                item_key: [

                ]
            }
            item[item_key].append(json_result)
        else:
            for search_glava in search_glavas:
                json_result = {
                    search_glava[0]: [

                    ]
                }
                item[item_key].append(json_result)

        for search_glava in item[item_key]:
            glava_key = [*search_glava][0]
            search_paragraphs = [list(result) for result in re.findall(r'Параграф(.*?)(?=(Параграф|$))', glava_key, re.DOTALL)]

            if not search_paragraphs:
                json_result = {
                    glava_key: [

                    ]
                }
                search_glava[glava_key].append(json_result)
            else:
                for search_paragraph in search_paragraphs:
                    json_result = {
                        search_paragraph[0]: [

                        ]
                    }
                    search_glava[glava_key].append(json_result)

            for search_paragraph in search_glava[glava_key]:
                paragraph_key = [*search_paragraph][0]
                search_statyas = [list(result) for result in re.findall(r'Статья(.*?)(?=(Статья|$))', paragraph_key, re.DOTALL)]

                if not search_statyas:
                    json_result = {
                        paragraph_key: [

                        ]
                    }
                    search_paragraph[paragraph_key].append(json_result)
                else:
                    for search_statya in search_statyas:
                        json_result = {
                            search_statya[0]: [

                            ]
                        }
                        search_paragraph[paragraph_key].append(json_result)

                for search_statya in search_paragraph[paragraph_key]:
                    statya_key = [*search_statya][0]
                    # search_punkts = re.findall(r'\d+\.\s[^\d]+(?:\d+\))?[^\d]+', statya_key)
                    search_punkts = re.split(r'\n\s*(?=\d+\.)', statya_key.strip())
                    search_punkts = [segment for segment in search_punkts if segment]
                    if not search_punkts:
                        json_result = {
                            str(statya_key): [

                            ]
                        }
                        search_statya[statya_key].append(json_result)
                    else:
                        for search_punkt in search_punkts:
                            json_result = {
                                str(search_punkt): [

                                ]
                            }
                            search_statya[statya_key].append(json_result)

                    for search_punkt in search_statya[statya_key]:
                        print(search_punkt)
                        punkt_key = [*search_punkt][0]
                        search_podpunkts = re.findall(r'\d+\)[^\d]*\s*\n?[^\d]*', punkt_key)
                        if search_podpunkts:
                            for search_podpunkt in search_podpunkts:
                                search_punkt[punkt_key].append(search_podpunkt)

    output_file_path = "output.json"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        json.dump(result, output_file, ensure_ascii=False, indent=2)