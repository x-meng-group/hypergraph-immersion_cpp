from Vector import vector


class sorted_array:

    def __init__(self, sorted_list: list, attribute: any, acending: bool = True):
        '''
        :param sorted_list: a list sorted by the attribute
        :param attribute: the attribute of the vector we are sorting by
        :param acending: True for acending order and false for decending order
        '''

        self.__array = sorted_list
        self.__attribute = attribute
        self.__acending = acending
        pass

    @classmethod
    def sort(cls, array: list, attribute: any, acending: bool = True):
        '''
        :param array: an unsorted list of vectors
        :param attribute: the attribute of the vector we are sorting by
        :param acending: True for acending order and false for decending order
        '''
        sorted_list = cls([], attribute, acending)

        # O(n)
        for v in array:
            sorted_list.insert(v) # O(log(n))
        
        # thus we have a final runtime of O(n * log(n))
        return sorted_list

    def __iter__(self):
        for i in self.__array:
            yield i
        pass

    def __str__(self):
        s = "["
        for i in self[0:-1]:
            s += str(i) + ", "
        if len(self) > 0:
            s += str(self[-1])
        return s + "]"

    def __len__(self):
        return len(self.__array)

    def __getitem__(self, index):
        return self.__array[index]
    
    def insert(self, item: vector) -> None:
        '''
        :param item: the vector you want to add to the list
        '''
        upper_bound = len(self)
        lower_bound = 0
        index = upper_bound // 2
        if self.__acending:
            while lower_bound < upper_bound:
                if item[self.__attribute] > self.__array[index][self.__attribute]:
                    lower_bound = index + 1
                else:
                    upper_bound = index
                index = (lower_bound + upper_bound) // 2
        else:
            while lower_bound < upper_bound:
                if item[self.__attribute] < self.__array[index][self.__attribute]:
                    lower_bound = index + 1
                else:
                    upper_bound = index
                index = (lower_bound + upper_bound) // 2
        self.__array.insert(lower_bound, item)
        pass

    def pop(self, index) -> vector:
        '''
        :param index: the index you want to remove
        '''
        return self.__array.pop(index)

    def multiinsert(self, L: any) -> None:
        '''
        :param L: any class that supports itteration
        '''
        for item in L:
            self.insert(item)
        pass

    def find_max(self, attribute: any) -> int | float:
        '''
        :param attribute: the attribute you want to maximize
        '''
        max_value = self[0][attribute]
        if len(self) > 1:
            for v in self[1:]:
                if v[attribute] > max_value:
                    max_value = v[attribute]
        return max_value
    
    def find_min(self, attribute: any) -> int | float:
        '''
        :param attribute: the attribute you want to minimize
        '''
        min_value = self[0][attribute]
        if len(self) > 1:
            for v in self[1:]:
                if v[attribute] < min_value:
                    min_value = v[attribute]
        return min_value
    
    def acending(self) -> bool:
        return self.__acending