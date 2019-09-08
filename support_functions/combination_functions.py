def calculate_next_combination(x,n):
    """
    for integer x, return integer iNext
    when x is described by binary form, x has i number of 1s.
    iNext is the smallest integer which is bigger than x and can be described by binary form using i number of 1s.
    if integer satisfying conditions is bigger than (2^n)-1, then iNext is the integer which can be described by binary form using i+1 num of 1s.
    for example, x = 100, x == 1100100(2). then iNext == 1101000(2) == 104
    """
    if n == 0:
        return False
    if x == 0:
        return(1)
 
    i_position_of_smallest_1 = 0
    i_position_of_smallest_0_after_first_1 = 0
    i_next = x
 
    while x%2 == 0:
        i_position_of_smallest_1 += 1
        x = x >> 1
    x = x >> 1
 
    while x%2 == 1:
        x = x >> 1
        i_next += pow(2,i_position_of_smallest_0_after_first_1) 
        i_next -= pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1)
        i_position_of_smallest_0_after_first_1 += 1
 
    if i_position_of_smallest_0_after_first_1 == n-1:
        #"every combinations are found"
        return False
    elif i_position_of_smallest_0_after_first_1 > n-1:
        #"it is over the combination range"
        return False
 
    if i_position_of_smallest_1 + i_position_of_smallest_0_after_first_1 == n-1:
        #"one combination ended"
        i_next += pow(2,i_position_of_smallest_0_after_first_1) 
        i_next += pow(2,i_position_of_smallest_0_after_first_1 +1) 
        i_next -= pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1)
    else:
        i_next -= pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1) 
        i_next += pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1+1)

    """
    #test code
    z=iNext
    k = ''
    while z:
        k+=str(z%2)
        z=z>>1
    print(k)
    """
    return i_next
