class Search(object) :

    def __init__(self, brand):
        self.brand = brand
        self._keyword = {}

    def add_group_keyword(self, groupName):
        self._keyword[groupName] = []

    def add_search_keyword(self, groupName, keywords):
        self._keyword[groupName].append(keywords)