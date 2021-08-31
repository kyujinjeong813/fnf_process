################## version 1. ##################
import random

# 캐릭터 클래스 작성
# 공통 속성 : HP, SP
# 공통 메서트 : 공격(대상 클래스 매개변수, HP차감), HP체크
class Character:
    def __init__(self, health_point=100, striking_point=3):
        self.health_point = health_point
        self.striking_point = striking_point

    def attack(self, object):
        object.health_point -= self.striking_point

    def checkHealthPoint(self):
        if self.health_point <= 0:
            print("DOOMED.")
        return self.health_point

# 인간 클래스 : 캐릭터 상속, 0~3 사이의 방어력 속성 추가, 공격 받았을 경우 방어함
class Human(Character):
    def __init__(self):
        super().__init__()
        self.defense_power = 3

    def defense(self):
        defense_prob = random.choice([0.3,0.6,0.8,1])
        defense_power = round(self.defense_power * defense_prob)
        return defense_power

# 몬스터 클래스 : 인간보다 공격력이 높음, 공격 함수에 다른 캐릭터 생길 가능성 고려, hasattr 사용
class Monster(Character):
    def __init__(self):
        super().__init__()
        self.striking_point = 5
    def attack(self, object):
        if hasattr(object, 'defense_power'):
            defense_power = object.defense()
            striking_point = self.striking_point - defense_power
            object.health_point -= striking_point
        else:
            object.health_point -= self.striking_point

# 10대 10이지만, 떼싸움이 아니기 때문에 목숨이 10개 있는 싸움으로 봐도 무방함
# 싸움 순서는 인간이 먼저 / 턴 바꿔가면서 공격하도록 초기 셋팅
# 한놈이 죽을때까지 싸움 > 결과값 리턴 > 목숨 카운트
class Game:
    def __init__(self):
        self.human_player = Human()
        self.monster_player = Monster()
        self.human_first = True
        self.human_life = 10
        self.monster_life = 10

    def play(self):
        while self.human_life > 0 and self.monster_life > 0:
            self.fight()
        if self.human_life <= 0:
            print("Monster Win!")
        elif self.monster_life <= 0:
            print("Human Win!")

    def fight(self):
        fight_in_process = True
        current_player = self.human_player
        while fight_in_process is True:
            if (current_player == self.human_player):
                current_player = self.monster_player
            else:
                current_player = self.human_player

            if (current_player == self.human_player):
                self.human_player.attack(self.monster_player)
                health_point = self.monster_player.checkHealthPoint()
                if health_point <= 0:
                    print("Monster.P is dead!")
                    self.monster_life -= 1
                    fight_in_process = False
            else:
                self.monster_player.attack(self.human_player)
                self.human_player.defense(self.monster_player)
                health_point = self.human_player.checkHealthPoint()
                if health_point <= 0:
                    print("Human.P is dead!")
                    self.human_life -= 1
                    fight_in_process = False
