import json

class task_list_:
    def __init__(self):
        self.data = {}
        with open('tasks.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            f.close()
        
        self.task_list = [] * 16

        list_of_tasks = self.data['task_list']

        self.task_list = [0] * 16

        for i in range (0, 16):
            task_num = list_of_tasks[i]['task_num']
            tasks = list_of_tasks[i]['tasks']
            curNum_task_array = []
            for j in range(len(tasks)):
                problem_text = tasks[j]['problem_text']
                answer = tasks[j]['answer_text']
                explanation = tasks[j]['explain_text']
                task = {}
                task['text'] = problem_text
                task['answer'] = answer
                task['explanation'] = explanation
                curNum_task_array.append(task)
            self.task_list[int(task_num) - 1] = curNum_task_array

def main():

    task_list = task_list_()
    print(task_list.task_list[0][0])
    input('Нажмите Enter для выхода\n')

if __name__ == '__main__':
    main()
