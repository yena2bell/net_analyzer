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


def generator_combination_num_in_defined_1(n,i_num_of_1):
    """ make generator giving integer which has 'i_num_of_1' of 1 when converted to binaray form.
    and that integer's binary form has digits lesser than n"""
    if n < i_num_of_1:
        raise ValueError("n should be larger or equal to i_num_of_1")
    if n<=0:
        raise ValueError("n shoule be larger than 0")
    
    i_position_of_smallest_1 = 0
    i_position_of_smallest_0_after_first_1 = int(i_num_of_1)
    i_combination = pow(2,int(i_num_of_1))-1
    i_end_combination = i_combination * pow(2,(int(n)-int(i_num_of_1)))
    
    yield i_combination
    
    while i_combination < i_end_combination:
        if i_position_of_smallest_0_after_first_1 == 1:
            i_combination += pow(2, i_position_of_smallest_1)
            i_position_of_smallest_1 += 1
        else:
            i_combination += pow(2, i_position_of_smallest_1+i_position_of_smallest_0_after_first_1-1)
            i_sum = i_position_of_smallest_1+i_position_of_smallest_0_after_first_1
            i_combination = (i_combination>>i_sum)*pow(2,i_sum) + pow(2, i_position_of_smallest_0_after_first_1-1) -1
            i_position_of_smallest_1 = 0
            
        i_position_of_smallest_0_after_first_1 = 1
        while (i_combination >> (i_position_of_smallest_1 + i_position_of_smallest_0_after_first_1))%2 == 1:
            i_position_of_smallest_0_after_first_1 += 1
        
        yield i_combination

        
            
        
        
    