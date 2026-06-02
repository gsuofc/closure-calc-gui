

import math

from closure_helper import compute_dd_from_dms, compute_dms_from_dd, compute_dxdy_from_curve_delta, compute_dxdy_from_straightline, is_number, safe_evaluate


class closure_calculator:
    def __init__(self,app):
        self.app = app
        self.currently_drawing = False
        self.closure_has_been_done = False
        self.closure_stats = {}
        self.distances = []
        self.direct_points = []

    def compute_closure(self, t, t2, tscreen):
        if self.currently_drawing:
            return
        self.currently_drawing = True
        self.distances = []
        self.direct_points = []
        x=0
        y=0
        prevx=0
        prevy=0
        bearing=0
        distance = 0

        radius = 0

        minx = -5
        miny = -5
        maxx = 5
        maxy = 5
        
        # Reset turtle
        t.pensize(2)
        t.color("blue")
        t.speed(0)

        t2.pensize(5)
        t2.color("red")
        t2.speed(0)

        tscreen.tracer(0)  # Turn off automatic screen updates

        for row_widgets in self.app.row_controller.rows:
            line_segment = {}
            curve_segment = {}

            is_curve = row_widgets["curve"].get()
            # Calculation depends on if the segment is a curve or a straight line
            if is_curve:
                d = row_widgets["deg"].get()
                m = row_widgets["min"].get()
                s = row_widgets["sec"].get()
                r = safe_evaluate(row_widgets["radius"].get(),self.app.settings.get_settings_option("enable_math_eval"))
                a = safe_evaluate(row_widgets["arc"].get(),self.app.settings.get_settings_option("enable_math_eval"))

                rd = row_widgets["rb_deg"].get()
                rm = row_widgets["rb_min"].get()
                rs = row_widgets["rb_sec"].get()

                curve_segment["rad-bear"] = False

                if is_number(rd) and is_number(rm) and is_number(rs):
                    # If a radial bearing is given, change the current bearing to that (otherwise use the last bearing as the starting bearing)
                    b = compute_dd_from_dms(float(rd),float(rm),float(rs))
                    b-=90
                    bearing = math.radians(b)
                    #Save radial bearing to file
                    curve_segment["rad-bear"] = True
                    curve_segment["rad-d"] = float(rd)
                    curve_segment["rad-m"] = float(rm)
                    curve_segment["rad-s"] = float(rs)

                if is_number(r):
                    radius = float(r)

                if is_number(d) and is_number(m) and is_number(s) and radius!=0:
                    # If interior angle is given, compute the curve from that
                    dd = compute_dd_from_dms(float(d),float(m),float(s))
                    if radius<0:
                        dd*=-1

                    (dx,dy,bearing_new) = compute_dxdy_from_curve_delta(bearing,math.radians(dd),radius)
                    x+=dx
                    y+=dy

                    t.seth((90-math.degrees(bearing))%360)
                    t.circle(radius,abs(dd))

                    bearing = bearing_new
                    distance+=abs(radius*math.radians(dd))

                    curve_segment["radius"] = radius
                    curve_segment["arc"] = radius*math.radians(dd)
                elif radius!=0 and is_number(a):
                    #if the arc length is given, convert to interior angle and then compute from that
                    rad = float(a)/radius
                    (dx,dy,bearing_new) = compute_dxdy_from_curve_delta(bearing,rad,radius)
                    x+=dx
                    y+=dy

                    t.seth((90-math.degrees(bearing))%360)
                    t.circle(radius,abs(math.degrees(rad)))

                    bearing = bearing_new
                    distance+=abs(float(a))

                    curve_segment["radius"] = radius
                    curve_segment["arc"] = float(a)
                
                # Save bearing after curve for file saving/drawing
                b_degrees = bearing*180/math.pi
                (b_d, b_m, b_s) = compute_dms_from_dd(b_degrees)
                curve_segment["bearing-d"] = float(b_d)
                curve_segment["bearing-m"] = float(b_m)
                curve_segment["bearing-s"] = float(b_s)

            else:
                # A straight line just uses the direct problem
                d = row_widgets["deg"].get()
                m = row_widgets["min"].get()
                s = row_widgets["sec"].get()
                di = safe_evaluate(row_widgets["distance"].get(),self.app.settings.get_settings_option("enable_math_eval"))

                # Reset the curve radius
                radius = 0

                if is_number(di):
                    # If a new bearing is given, use that as the bearing. Otherwise reuse the last bearing
                    if is_number(d) and is_number(m) and is_number(s): 
                        b = compute_dd_from_dms(float(d),float(m),float(s))
                        bearing = math.radians(b)
                    
                    (dx,dy,bearing_new) = compute_dxdy_from_straightline(bearing,float(di))

                    t.seth((90-math.degrees(bearing_new))%360)
                    t.forward(float(di))

                    x+=dx
                    y+=dy
                    bearing = bearing_new

                    if float(di)<0:
                        # If a distance is negative, treat that as 180 in the other way
                        bearing+=math.radians(180)

                    distance+=abs(float(di))

                    # Save distance and bearing to file to save/display
                    line_segment["distance"] = abs(float(di))
                    b_degrees = bearing*180/math.pi
                    (b_d, b_m, b_s) = compute_dms_from_dd(b_degrees)
                    line_segment["bearing-d"] = float(b_d)
                    line_segment["bearing-m"] = float(b_m)
                    line_segment["bearing-s"] = float(b_s)

                        
            # Update bounds of screen
            if x < minx:
                minx = x
            if y < miny:
                miny = y
            if x > maxx:
                maxx = x
            if y > maxy:
                maxy = y

            # Compute ranges
            xrange = maxx - minx
            yrange = maxy - miny
            padding = 1.4

            # Use the largest of the two ranges for a square view
            max_range = max(xrange, yrange) * padding

            # Compute midpoints
            xmid = (minx + maxx) / 2
            ymid = (miny + maxy) / 2

            # Swap x and y deliberately for coordinate system
            # y becomes horizontal (left/right), x becomes vertical (bottom/top)
            tscreen.setworldcoordinates(
                ymid - max_range / 2,  # left (x-axis, actually y)
                xmid - max_range / 2,  # bottom (y-axis, actually x)
                ymid + max_range / 2,  # right
                xmid + max_range / 2   # top
            )
            t2.penup()
            t2.goto(y,x)
            t2.dot(10,"red")

            while bearing<0:
                bearing+=math.radians(360)

            if prevx!=x or prevy!=y:
                coords = {
                    'x': x,
                    'y': y,
                    'is_curve': is_curve
                }
                if is_curve:
                    coords["curve_segment"] = curve_segment
                else:
                    coords["line_segment"] = line_segment
                self.direct_points.append(coords)

            prevx=x
            prevy=y

        dist = math.sqrt(x**2+y**2)
        # dist = final displacement, distance = sum of lengths of the segments

        closure = float('inf')      
        # To avoid a /0 error, only divide if dist is not equal to 0. (closure is listed as 1/n and a perfect closure means 1/0)
        if dist!=0:
            closure = distance/dist

        while bearing>2*math.pi:
            bearing-=2*math.pi

        b_degrees = bearing*180/math.pi

        (b_d, b_m, b_s) = compute_dms_from_dd(b_degrees)

        t.color("black")
        t.write("Closure: 1/%.0f \nd:%.3f di: %.3f\n(x: %.3f, y: %.3f)\nBearing: %d-%d-%.3f"%(closure,dist,distance,x,y,b_d,b_m,b_s))


        tscreen.update()  # Turn off automatic screen updates

        self.closure_stats = {
            "closure":closure,
            "displacement":dist,
            "distance":distance,
            "x":x,
            "y":y,
        }
        self.app.rebind_turtle_controls(tscreen.getcanvas())

        self.currently_drawing = False
        self.closure_has_been_done = True

    def has_closure_results(self):
        return self.closure_has_been_done