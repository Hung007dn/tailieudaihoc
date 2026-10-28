#Vũ Trọng Hưng 24162053
class Queue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = []

    def isEmpty(self):
        return len(self.queue) == 0

    def isFull(self):
        return len(self.queue) == self.capacity

    def enqueue(self, value):
        if self.isFull():
            print("Queue đầy, không thể enqueue!")
        else:
            self.queue.append(value)
            print(f"Đã thêm {value} vào queue")

    def dequeue(self):
        if self.isEmpty():
            print("Queue rỗng, không thể dequeue!")
            return None
        else:
            return self.queue.pop(0)

    def front(self):
        if self.isEmpty():
            print("Queue rỗng, không có phần tử đầu!")
            return None
        return self.queue[0]
q = Queue(3)

q.enqueue(10)
q.enqueue(20)
q.enqueue(30)
q.enqueue(40)   # vượt capacity

print("Front:", q.front())

print("Dequeue:", q.dequeue())
print("Dequeue:", q.dequeue())
print("Dequeue:", q.dequeue())
print("Dequeue:", q.dequeue())  # queue rỗng
