import math
import re


def compute_dxdy_from_straightline(rads,di):
    # Using a distance and angle, compute the next set of coords (direct problem)
    (dx,dy) = compute_direct(di,rads)

    return (dx,dy,rads)

def compute_dxdy_from_curve_delta(rad_bearing,rad,r):
    # Using a starting bearing, curve radius and bearing, compute the next set of coords
    # This is done by going towards the radius, adding the angle, and then going going away
    bearing_towards = rad_bearing-math.radians(90)
    bearing_away = bearing_towards-math.radians(180)-rad
    bearing_new = bearing_away-math.radians(90)

    (dx1,dy1) = compute_direct(r,bearing_towards)
    (dx2,dy2) = compute_direct(r,bearing_away)

    dx = dx1+dx2
    dy = dy1+dy2

    return (dx,dy,bearing_new)

def compute_direct(dist,rad):
    # Computes the direct problem (give change in distance using distance and radius)
    dx = dist*math.cos(rad)
    dy = dist*math.sin(rad)

    return (dx,dy)

def compute_dms_from_dd(dd, round_off = True):
    b_d = math.floor(dd)
    b_min = (dd-b_d)*60
    b_m = math.floor(b_min)
    b_s = (b_min-b_m)*60
    if round_off:
        #check to see if seconds rounds to 60 - if so fix
        rounded_s = round(b_s, 3)
        if rounded_s >=60.0:
            b_m +=1
            b_s -=60
            if b_m >= 60.0:
                b_d +=1
                b_m -=60
                if b_d >= 360.0:
                    b_d-=360

        #given that if we do the above, 59.9999 will become -0.0001. This will round to -0, we would rather just have 0. 
        if b_d < 0:
            b_d = 0
        if b_m < 0:
            b_m = 0
        if b_s < 0:
            b_s = 0
        #Perhaps there is a better way of doing this - maybe having rounding as arguement rather than being hardcoded? TODO: 
        #For now adding default argument in case I want to not do this

    return (b_d, b_m, b_s)

def compute_dd_from_dms(d,m,s):
    #TODO: Check for negative DMS
    dd = d
    dd += m/60
    dd += s/(60*60)
    return dd

def safe_evaluate(expression, enabled = True):
    if not enabled:
        return expression

    # Rather than passing any user input we see if 
    if not re.match(r"^[0-9+\-*/().\s]+$", expression):
        return expression # Possibly raise an error but at this point we only care for a value 
    
    try:
        #cleaned_expr = re.sub(r'\b0+(?=\d)', '', expression)
        evalued =  eval(expression)
        return evalued
    except:
        print("Error with eval: %s"%expression)
        return expression
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
