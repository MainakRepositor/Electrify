import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
###NOTE will need to "pip install schemdraw" to see the diagram

import schemdraw
import schemdraw.elements as elm
from schemdraw.elements import Resistor as R
st.sidebar.image('logo.jpg')
st.title("Smart Circuit Simulation")


st.markdown("$\colorbox{blue}{-}$ $\large\\textnormal{ Open the sidebar in the top left to get started!}$", unsafe_allow_html = True)

sidebar = st.sidebar
with sidebar: #everything in the following scope of this with statement will be in the sidebar

    num_r = int( st.number_input(label = "Select Number of Resistors",\
    min_value = 1, max_value = 9, value = 2) )
    #Setting the bounds to 0 and 7 resistors with the program defaulting to 1 resistor.
    #holding the number of resistors selected in the variable num_r as an integer.
    par_series = st.checkbox(label = "Select for parallel circuit.")
    if par_series:
        #If there is more than one resistor the user has the option to make the resistors parallel
        #note to accomodate this I made the default number of resisitors 2, becuase the button
        #only appears if there is more than one resistor
        num_paths = int( st.number_input(label = "Select number of paths.",\
        min_value = 2, max_value = num_r) )
        #usre selects the nujmber of paths in the parallel cirucit
        num_r_per_path = [] #Initializing a a list to hold the number of resistors per enumerated oath
                                          #I will use the index of each integer to keep track of which path is which
                                          ##Note this updates every time something changes.
        num_r_left = num_r #Initializing a variable to hold the number of resistors the user has left to place
        for i in range(num_paths): #Loop will allow the user to choose how many resistors per path
            if num_r_left == 0:
                break #If there are no more resistors left, even if there are still paths, the loop will break

            elif num_r_left > 0 and i == num_paths - 1:
                #if there is only one path remaining, all the remaning resistors will be dumped into it.
                numero_de_r_par_chemin = int( st.number_input(label= f"Remaining Resistors in final path #{i+1}:" ,\
                min_value = num_r_left, max_value = num_r_left) )
                num_r_per_path.append(numero_de_r_par_chemin)
                break

            numero_de_r_par_chemin = int(st.number_input(label = f"Select number of resistors for path #{i+1}:",\
            min_value = 1, max_value = num_r_left))
            #This variable is how many resistors they want in each path.
            num_r_per_path.append(numero_de_r_par_chemin) #Appends the variable above to a list to hold it
            num_r_left -= numero_de_r_par_chemin #Keep track of how many resistors are available
    #Will define function(s) that will calculate the total current and the voltage drop at each resistor.

    st.markdown("Select Input Voltage (**V**):")
    voltage = st.columns(2)
    with voltage[0]:
        volt1 = st.slider(label = "Macro slider:", min_value = 0, max_value = 10000, step = 100)
        #on_change = )
    with voltage[1]:
        volt2 = st.slider(label = "Micro slider:", min_value = 0, max_value = 100, step = 1)

    input_v = volt1 + volt2
    f"Current Voltage Input is **{input_v}** **V**"

####Helper function
def ohm_input(num_r, ith_resistor): #Making a helper function to make life easier
    '''
    (int, int) -> list

    This function takes a number of resistors. Also asks for "ith_resistor" which is used to
    keep track of which resistor is being modified in order to maintain uniqueness of st.number_input keys
    It then asks to input the resistance of each resistor.
    Returns their resistance in order of Resistor 1 to Resistor num_r inside a list.

    Note: Requires ith_resistor to be intialized to 0 when used for the first instance.
    '''
    #Separates the UI into rows with max three columns of resistors each
    if num_r > 6:
        col1 = st.columns(3)
        col2 = st.columns(3)
        col3 = st.columns(3)
    elif num_r > 3:
        col1 = st.columns(3)
        col2 = st.columns(3)
    else:
        col1 = st.columns(3)
    #Above is all circumstancial depending on how many resistors they have.
    ohm_per_r = [] #Initializing list to hold the resistance of each resistor
    for res in range(int(num_r)):
        if res in range(0, 3):
            with col1[res]:
                ohm_per_r.append( st.number_input(label = f"Resistor {ith_resistor + 1}",\
                min_value = 1, max_value = 10000, key = ith_resistor) )
        elif res in range(3, 6):
            with col2[res % 3]:
                ohm_per_r.append( st.number_input(label = f"Resistor {ith_resistor + 1}",\
                min_value = 1, max_value = 10000, key = ith_resistor) )
        elif res in range(6,9):
            with col3[res % 3]:
                ohm_per_r.append(st.number_input(label = f"Resistor {ith_resistor + 1}",\
                min_value = 1, max_value = 10000, key = ith_resistor))

        ith_resistor += 1 #Increment which resistor we are at every time
    #Returning a tuple of a list and int
    return ohm_per_r, ith_resistor

####Helper function 2
def resistance_counter(path, num_r_per_path, ohm_per_r):
    '''
    (int or float, int, int, list, list) -> int

    This function takes the current, input voltage and path in question along with the lists
    that hold the number of resistors per path and the resistance per resistor.

    Returns the total resistance on the given path.
    '''
    list_resistors_in_path = ohm_per_r[ int( sum( num_r_per_path[ : path] ) ) :\
    int( sum( num_r_per_path[ : path]) + num_r_per_path[path] ) ]
    resistance = int( sum( list_resistors_in_path) )

    return resistance, list_resistors_in_path

####Helper function 3
def circuit_drawer(num_r, ohm_per_r, current, list_pathway_current = None, num_r_per_path = None):
    '''
    (int, list, float or int[, list, list] ) -> schemdraw diagram

    Function takes the number of resistors, the list of their resistances, the total current
    and the list of pathway currents and the list of the number of resistors on each path
    which is optional because of series circuits only having one path.
    '''
    with schemdraw.Drawing() as s: #creating a schemdraw figure and declaring it as s

        if current < 1: #turning the current into a printable form for the diagram
            string_current = str(round( current * 1000, 4) ) + "mA" #milliAmperes
        else:
            string_current = str(round( current, 4) ) + "A"

        s.config(unit=2) #This makes the length of the objects shorter to take less place
        s.add( Dot1 := elm.Dot())
        s.add(V := elm.SourceV().label(str(input_v) + "V"))
        s += elm.Dot().label("Path 1", loc = "left")

        if list_pathway_current == None: #series circuit
            if num_r > 6: #more than 6
                for i in range(3):
                    s.add( R( label = str(ohm_per_r[i]) + "Ω"))

                s += elm.Dot()
                for i in range(3,6):
                    s.add(R(label = str(ohm_per_r[i]) + "Ω").right())

                s += elm.Dot()
                for i in range(6, num_r):
                    s.add(R( label = str(ohm_per_r[i]) + "Ω").down())

                s += elm.Line().toy(V.start) #draws a line until it is at the same height as the battery
                s.add(elm.SourceI().label(string_current, loc="bottom").left()) #Adds an Ammeter
                s += elm.Line().tox(Dot1.center)

            elif num_r > 4: #more than 4
                for i in range(2):
                    s.add( R( label = str(ohm_per_r[i]) + "Ω"))

                s += elm.Dot()
                for i in range(2,4):
                    s.add(R(label = str(ohm_per_r[i]) + "Ω").right())

                s += elm.Dot()
                for i in range(4,num_r):
                    s.add(R( label = str(ohm_per_r[i]) + "Ω").down())

                s += elm.Line().toy(V.start) #draws a line until it is at the same height as the battery
                s.add(elm.SourceI().label(string_current, loc="bottom").left()) #Adds an Ammeter
                s += elm.Line().tox(Dot1.center)

            elif num_r > 2: #more than 2
                for i in range(2):
                    s.add( R( label = str(ohm_per_r[i]) + "Ω"))

                s += elm.Dot()
                for i in range(2,num_r):
                    s.add(R(label = str(ohm_per_r[i]) + "Ω").right())

                s += elm.Dot()
                s += elm.Line().toy(V.start) #draws a line until it is at the same height as the battery
                s.add(elm.SourceI().label(string_current, loc="bottom").left()) #Adds an Ammeter
                s += elm.Line().tox(Dot1.center)

            else: #less than 2
                for i in range(num_r):
                    s.add( R( label = str(ohm_per_r[i]) + "Ω"))
                s += elm.Dot()
                s += elm.Line().right()
                s += elm.Line().toy(V.start) #draws a line until it is at the same height as the battery
                s.add(elm.SourceI().label(string_current, loc="bottom").left()) #Adds an Ammeter
                s += elm.Line().tox(Dot1.center)


        else: # parallel circuit
            lst = [] #making a list to hold the string expressions of the pathway currents
            for pathway_current in range(len(list_pathway_current)):
                if list_pathway_current[pathway_current] < 1:
                    lst.append(str(round(list_pathway_current[pathway_current], 4)) + "mA")
                else:
                    lst.append(str(round(list_pathway_current[pathway_current], 4)) + "A")

            ith_resistor = 0 #keeps track of which resistor we are at
            for path_number in range(len(list_pathway_current)): #number of paths to loop for
                s.push() #this works with s.pop() and allows me to change direction of pathways
                #without affecting direction of entire circuit

                for r in range(num_r_per_path[path_number]): #this loops through the resistors in a given path
                    s.add(R( label = str(ohm_per_r[ith_resistor]) + "Ω").right())
                    ith_resistor += 1 #increment the resistor number by one
                s.add(elm.SourceI(label = lst[path_number]).right()) #adds ammeter with pathway current reading
                #four lines below just attach to main circuit again

                for line_to_draw in range(max(num_r_per_path) - num_r_per_path[path_number]):
                    s += elm.Line().right()
                s += elm.Dot()
                s += elm.Line().toy(V.start)
                if path_number == 0:
                    s.add(Dot2 := elm.Dot()) #declaring this as Dot2 so that I can place my total ammeter next to it
                else:
                    s += elm.Dot()
                s += elm.Line().tox(Dot2.center)

                s.pop()

                if path_number < len(list_pathway_current) - 1:
                    s += elm.Line() #makes a line so that the next path can branch off
                    s += elm.Dot().label(f"Path {path_number + 2}", loc = "left")

            s.add(elm.SourceI().label("Total: " + string_current, loc="bottom").endpoints(Dot2.center ,Dot1.center)) #Adds an Ammeter for total current
        image = s.get_imagedata('jpg')

    st.image(image)

##### End of helper functions


ith_resistor = 0 #Declaring this variable because parallel circuits caused problems with the
#uniqueness of each st.number_input call in my helper function above.
#I am using it to keep track of which resistor is being considered

voltage_drop_at_ith_resistor = [] #List to hold this information organized by index

if not par_series: #user selects series circuit
#note that par_series refers to the checkbox in the sidebar.
    "$\colorbox{red}{-}$" f" Select resistance for the {num_r} resistor(s) ($\Omega$)"
    #Used LaTex for the ohms unit.
    ohm_per_r = ohm_input(num_r, ith_resistor)[0]
    #If it is series, I do not need the ith_resistor variable
    ""
    "$\Large\mathrm{Results}$"

    current = input_v / sum(ohm_per_r) #The total current

    for resistor in ohm_per_r: #The voltage drop
        voltage_drop_at_ith_resistor.append(current * resistor)
        #Appends the voltage drop of each resistor to the list in order.

    c = st.columns(3) #making columns to make UI look nicer
    with c[0]:
        "$\colorbox{yellow}{-}$" f" Total input voltage: {input_v} **V**"
    with c[1]:
        "$\colorbox{lightgreen}{-}$" " Total resistance: " + str(int(sum(ohm_per_r))) + " $\Omega$"
    with c[2]:
        if current < 1:
            "$\colorbox{green}{-}$" " Total current: " + str(round( current * 1000, 4) ) + " m$\Alpha$"
        else:
            "$\colorbox{green}{-}$" " Total current: " + str(round( current, 3) ) + " $\Alpha$"

else: #User selects parallel circuit:
    ohm_per_r = [] #Initializing list to hold the resistance of each resistor
    list_pathway_current = [] #initializing list to hold the pathway currents for later use in diagrams
    #updates with every change

    for path in range(len(num_r_per_path)): #loops for every path there is.
        with st.container(): #Creates a container for every path
            "$\colorbox{red}{-}$" f" Select resistance for the {num_r_per_path[path]} resistor(s) in Path {path+1} ($\Omega$):"

            list_of_resistances_per_path, ith_resistor = ohm_input(num_r_per_path[path], ith_resistor)
            #This function call uses how many resistors there are per path and the lates version of ith_resistor
            #Stores the returned values in the tuple declared
            for resistance in list_of_resistances_per_path:
                ohm_per_r.append( resistance )
                #appends to the list so I have them organized in order
    ""
    "$\Large\mathrm{Results}$"

    c = st.columns(3) #making columns to make UI look nicer
    with c[0]:
        "$\colorbox{yellow}{-}$" f" Total input voltage = {input_v} **V**"

    current = 0 #initialize current variable
    ith_resistor = 0
    for path in range(len(num_r_per_path)):
        resistance, list_resistors_in_path = resistance_counter(path, num_r_per_path, ohm_per_r)
        pathway_current = input_v/resistance #The current on each pathway
        list_pathway_current.append(pathway_current) #appends the individual path currents in order

        for impetus in list_resistors_in_path: #Will calculate voltage drop at each resistor and append to list below
            voltage_drop_at_ith_resistor.append(pathway_current * impetus)

        with c[2]: #Denoting the individual pathwat currents:
            if pathway_current < 1:
                "$\colorbox{teal}{-}$" f" Current Path {path+1} = " + str(round(pathway_current, 4)) + " m$\Alpha$"
            else:
                "$\colorbox{teal}{-}$" f" Current Path {path+1} = " + str(round(pathway_current, 4)) + " $\Alpha$"

        with c[1]:
            "$\colorbox{lightgreen}{-}$" f" Resistance Path {path+1} = {resistance}" + " $\Omega$"

        current += pathway_current #Sums pathway current to find total curent.

    with c[2]:
        if current < 1:
            "$\colorbox{pink}{-}$" " Total current = " + str(round( current * 1000, 4) ) + " m$\Alpha$"
        else:
            "$\colorbox{pink}{-}$" " Total current = " + str(round( current, 3) ) + " $\Alpha$"


"**Voltage Drop at Each Resistor:**"
if num_r > 6:
    column1 = st.columns(3)
    column2 = st.columns(3)
    column3 = st.columns(3)
elif num_r > 3:
    column1 = st.columns(3)
    column2 = st.columns(3)
else:
    column1 = st.columns(3)
#Above is all circumstancial depending on how many resistors they have.

for volt_drop in range(len(voltage_drop_at_ith_resistor)):
    if volt_drop in range(0, 3):
        with column1[volt_drop]:
            "$\colorbox{orange}{-}$"\
            f" Drop at R{volt_drop+1} = {round(voltage_drop_at_ith_resistor[volt_drop],3)} **V**"
    elif volt_drop in range(3, 6):
        with column2[volt_drop % 3]:
            "$\colorbox{orange}{-}$"\
            f" Drop at R{volt_drop+1} = {round(voltage_drop_at_ith_resistor[volt_drop],3)} **V**"
    elif volt_drop in range(6,9):
        with column3[volt_drop % 3]:
            "$\colorbox{orange}{-}$"\
            f" Drop at R{volt_drop+1} = {round(voltage_drop_at_ith_resistor[volt_drop],3)} **V**"
##Loop above prints displays the voltage drop at each resistor
""
""

st.markdown("$\colorbox{purple}{-}$ $\large\\textnormal{ Circuit:}$", unsafe_allow_html = True)
if not par_series: #series circut
    circuit_drawer(num_r, ohm_per_r, current)
else: #parallel circuit
    circuit_drawer(num_r, ohm_per_r, current, list_pathway_current, num_r_per_path)

""
st.markdown("$\colorbox{purple}{-}$ $\large\\textnormal{ Graph:}$", unsafe_allow_html = True)
fig,ax = plt.subplots(1)
ax.set_ylabel("Voltage (V)", fontsize = 12)
ax.set_xlabel("Resistor Number", fontsize = 12)

if not par_series:
    y_values = [input_v] #initialize a y valuess list with the initial voltage as the first y value
    for res in range(1, num_r + 1):#loop for every resistor there is
        #the plus 1 is to avoid a math operation in every loop,
        #essentially just backend optimization
        y_values.append(input_v - sum(voltage_drop_at_ith_resistor[:res]))
        #append the input voltage minus the sum of all the voltage drops up to the given resistor

    ax.plot(y_values, "r--o")
    ax.set_xticks(np.arange(1,num_r+1))
    ax.set_title("Total Voltage vs Resistor in Series", fontsize=16)
    ax.set_ylim(0)
else: #parallel circuits
    ith_resistor = 0 #keeps track of which resistor the loop is at.
    for i in range(len(num_r_per_path)): #loops for every path
        vdrop_values = [0] #initalize a list that holds the voltage drop at the zeroth resistor which is 0V
        y_values = [input_v] #initialize a y valuess list with the initial voltage as the first y value
        for j in range(num_r_per_path[i]): #loops for every resistor in a given path
            vdrop_values.append(voltage_drop_at_ith_resistor[ith_resistor])
            #append the voltage drop at the given ith_resistor to the voltage drop list
            y_values.append(input_v - sum(vdrop_values))
            #the y values is the input voltage - the sum of the voltage drops on the path up to the ith_resistor
            ith_resistor += 1 #increment by one

        x_values = list( range( sum(num_r_per_path[:i]), sum(num_r_per_path[:i+1]) + 1) )
        #the sum just tallies up all the resistors up to the given path and then including the path
        #then I make a range between those two values
        #x values is a list from the first resistor on path to the last resistor on the path
        ax.plot(x_values, y_values, "--o", label = f"Path {i+1}")
    ax.set_xticks(np.arange(1,ith_resistor))
    ax.set_ylim(0)
    ax.set_title("Total Voltage vs Parallel Resistors on a Given Path", fontsize = 14)
    ax.legend()
fig.tight_layout()
st.pyplot(fig)
