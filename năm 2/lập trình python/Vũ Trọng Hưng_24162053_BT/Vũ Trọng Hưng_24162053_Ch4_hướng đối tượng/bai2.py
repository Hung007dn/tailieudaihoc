#Vũ Trọng Hưng 24162053
class Stack:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def isEmpty(self):
        return len(self.items) == 0

    def isFull(self):
        return len(self.items) == self.capacity

    def push(self, value):
        if self.isFull():
            print("Error: Stack is full, cannot push!")
        else:
            self.items.append(value)

    def pop(self):
        if self.isEmpty():
            print("Error: Stack is empty, cannot pop!")
            return None
        else:
            return self.items.pop()

    def top(self):
        if self.isEmpty():
            print("Error: Stack is empty, no top element!")
            return None
        else:
            return self.items[-1]

    def display(self):
        if self.isEmpty():
            print("Stack is empty")
        else:
            print("Stack (bottom → top):", self.items)



if __name__ == "__main__":
    stack = Stack(3)

    
    stack.push(10)
    stack.push(20)
    stack.push(30)

   
    stack.push(40)   

 
    stack.display()

    print("Top element:", stack.top())

    print("Pop:", stack.pop())
    print("Pop:", stack.pop())
    print("Pop:", stack.pop())

    print("Pop:", stack.pop())  