#Vũ Trọng Hưng 24162053
class Person:
    def __init__(self, name, yob):
        self.name = name
        self.yob = yob

    def describe(self):
        return f"Name: {self.name}, Year of Birth: {self.yob}"


class OccupationPerson(Person):
    def __init__(self, name, yob, role, extra):
        super().__init__(name, yob)
        self.role = role          # "Student", "Teacher", "Doctor"
        self.extra = extra        # grade / subject / specialist

    def describe(self):
        return f"{self.role} - Name: {self.name}, Year of Birth: {self.yob}, Info: {self.extra}"


class Ward:
    def __init__(self, name):
        self.name = name
        self.people = []

    def addPerson(self, person):
        self.people.append(person)

    def describe(self):
        print(f"Ward: {self.name}")
        for p in self.people:
            print(p.describe())

    def countDoctor(self):
        return sum(p.role == "Doctor" for p in self.people)

    def sortAge(self):
        self.people.sort(key=lambda p: p.yob)

    def aveTeacherYearOfBirth(self):
        teachers = [p.yob for p in self.people if p.role == "Teacher"]
        if teachers:
            return sum(teachers) / len(teachers)
        return None



if __name__ == "__main__":
    ward = Ward("Dong Hoa Ward")

    ward.addPerson(OccupationPerson("An", 2005, "Student", "10A1"))
    ward.addPerson(OccupationPerson("Binh", 1980, "Teacher", "Math"))
    ward.addPerson(OccupationPerson("Lan", 1985, "Teacher", "Literature"))
    ward.addPerson(OccupationPerson("Minh", 1975, "Doctor", "Cardiology"))
    ward.addPerson(OccupationPerson("Hoa", 1990, "Doctor", "Pediatrics"))

    print("=== Thông tin Ward ===")
    ward.describe()

    print("\nSố lượng Doctor:", ward.countDoctor())

    ward.sortAge()
    print("\nSau khi sắp xếp theo tuổi tăng dần:")
    ward.describe()

    print("\nNăm sinh trung bình của Teacher:", ward.aveTeacherYearOfBirth())