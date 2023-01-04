import json

def main():
    with open('score.json', 'w') as f:
        json.dump({}, f, indent=4)
        data = {
            "task_list" : {}
            }
        for i in range(1, 16):
            data["task_list"][i] = {
                "right_answers" : 0,
                "total_answers" : 0
            }
        json.dump(data, f, indent=4)
        f.close()

    with open('score.json', 'r+') as f:
        data = f.read()
        f.seek(0)
        f.write(data[2:])
        f.truncate()
        f.close()

if __name__ == '__main__':
    main()
