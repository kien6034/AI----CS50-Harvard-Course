set1  = [(1, 2), (2,3)]
set2 = [(2,3), (1,2)]

s1 = set(set1)
s2 = set(set2)
print(s1 == s2)
print(s1.issubset(s2))