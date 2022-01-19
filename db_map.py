from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import *

engine = create_engine('postgresql:///vstup_TG')

Base.metadata.create_all(engine)


class DatabaseMapper():

    def __init__(self):

        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def add_area(self, name, code):

        area = self.session.query(Knowledge_area).filter_by(code=code).first()

        if not area:
            area = Knowledge_area(name=name, code=code)
            self.session.add(area)
            self.session.commit()

    def add_speciality(self, spec):

        code = spec['area']
        area = self.session.query(Knowledge_area).filter_by(code=code).first()
        speciality = self.session.query(
            Speciality).filter_by(name=spec['name']).first()

        if not speciality:

            '''
            If we haven't data about contract rating last year
            we set default 110 bcs when we will calculate chances
            we will deduct 10
            '''
            if not spec.get('contract'):
                spec['contract'] = 110

            speciality = Speciality(name=spec['name'], area=area,
                                    program=spec['program'],
                                    min_rate_budget=spec['budget'],
                                    min_rate_pay=spec['contract'])
        self.session.add(speciality)
        self.session.commit()

    def write_coefficients(self, znos, spec):

        speciality = self.session.query(
            Speciality).filter_by(name=spec['name']).first()

        # Write every coefficient from list to database
        for zno in znos:
            zno_subj = self.session.query(
                Zno).filter_by(name=zno['name']).first()

            if not zno_subj:
                zno_subj = Zno(name=zno['name'])
                self.session.add(zno_subj)

            coef = self.session.query(Coefficient).filter_by(
                zno=zno_subj).filter_by(speciality=speciality).first()
            if not coef:

                coef = Coefficient(zno=zno_subj,
                                   speciality=speciality,
                                   coefficient=zno['coefficient'],
                                   required=zno['required'])
                self.session.add(coef)

            else:
                if coef.coefficient != float(zno['coefficient']):
                    coef.coefficient = zno['coefficient']

            self.session.commit()

    def create_user(self, tg_id):
        ''' Create user if doesn't exist '''

        user = self.session.query(Users).filter_by(tg_id=tg_id).first()

        if not user:
            user = Users(tg_id=tg_id)

            self.session.add(user)
            self.session.commit()

    def get_grades(self, user):

        grades = self.session.query(Users).filter_by(tg_id=user).first().grades
        return (str(grade) for grade in grades)

    def set_grade(self, user, data):

        user = self.session.query(Users).filter_by(tg_id=user).first()
        zno = self.session.query(Zno).filter_by(name=data['name']).first()
        grade = self.session.query(Grades).filter_by(owner_id=user.id, zno=zno).first()

        if not grade:

            # check availability of grade at the user
            if data['grade'] != 0:
                grade = Grades(owner=user, grade=data['grade'], zno=zno)
                self.session.add(grade)
                self.session.commit()
                return 'Оцiнка успiшно додана'
            else:
                return 'У вас ще немає оцiнки з цього предмету.'

        else:
            if data['grade'] == 0:
                self.session.delete(grade)
                self.session.commit()
                return 'Оцiнка успiшно видалена.'
            else:
                grade.grade = data['grade']
                self.session.commit()
                return 'Оцiнка успiшно оновлена.'

    def all_znos(self):

        znos = self.session.query(Zno).all()

        return [str(zno) for zno in znos]

    def all_areas(self):

        areas = self.session.query(Knowledge_area).all()

        return [area for area in areas if area.specialities]

    def specs(self, areaz: int):

        area = self.session.query(Knowledge_area).filter_by(id=areaz).first()

        specs = self.session.query(Speciality).filter_by(area=area).all()

        return [spec for spec in specs]

    def grades_for_spec(self, tg_id, spec=None, area=None):

        user = self.session.query(Users).filter_by(tg_id=tg_id).first()

        # check mode from obtained data
        # if bot sent spec we will check for only 1 speciality
        if spec:
            speciality = self.session.query(Speciality).filter_by(id=spec).first()
            coefs = self.session.query(Coefficient).filter_by(
                speciality=speciality)
            grade = self.checking(user, coefs)

            if grade >= speciality.min_rate_budget:
                return 'Вiтаємо! Ви можете поступити на бюджет'

            # We have only avg contract score, so minimum can be 10 less.
            if grade >= (speciality.min_rate_pay - 10):

                return 'Вiтаємо! Ви можете поступити за контрактом'
            else:

                return 'Нажаль ви не можете поступити за цiєю спецiальнiстю'

        # if bot sent area we will check for all specialities in area
        else:
            area = self.session.query(Knowledge_area).filter_by(id=area).first()
            specs = area.specialities
            budget = []
            contract = []
            for spec in specs:

                coefs = self.session.query(Coefficient).filter_by(
                    speciality=spec)  # getting coefs by query bcs another case we're getting Instrumentallist
                grade = self.checking(user, coefs)  # get user grades

                if grade >= spec.min_rate_budget:
                    budget.append(spec.name)

                # We have only avg contract score, so minimum can be 10 less.
                if grade >= (spec.min_rate_pay - 10):
                    contract.append(spec.name)

            return {'budget': budget, 'contract': contract}

    def checking(self, user, coefs):

        req_cfs = coefs.filter_by(required=True).all()  # Getting required ZNO
        not_req = coefs.filter_by(required=False).all()  # Not required
        grade = 0  # start point
        # Checking availability required grade for user.
        for req in req_cfs:
            user_grade = self.session.query(Grades).filter_by(
                zno=req.zno, owner=user).first()
            if user_grade:
                # getting sum of required grades
                grade = grade + user_grade.grade * req.coefficient
            else:
                return 0

        ''' Getting maximum grade from additional znos '''
        max_third = 0
        for unreq in not_req:
            user_grade = self.session.query(Grades).filter_by(
                zno=unreq.zno, owner=user).first()
            if user_grade:
                if user_grade.grade > max_third:
                    max_third = user_grade.grade

        if max_third == 0:
            return 0

        # sum of scores of 2 required and third zno multiply for coefficients
        # 1.02 - regional coefficient for the major part of cities in UA
        grade = (grade + max_third * not_req[0].coefficient) * 1.02

        return grade
