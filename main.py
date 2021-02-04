import pygame
from pygame import locals
import serial
import numpy as np
import json
import ast
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

tk_root = Tk()
tk_root.withdraw()

s = serial.Serial("COM3", 115200)

last_ser = []
database = []

pygame.init()
screenwidth = 1100; screenheight = 300
screen = pygame.display.set_mode([screenwidth, screenheight])
pygame.display.set_caption("Kolorimeter controller")

x               = [] #here
y               = [] #here

stigningstall = 0
konstantledd  = 0

def add_regression_point(x_, y_): #here

    x.append(x_); y.append(y_)

def text(value, size, color, x, y):

    FONT = pygame.font.Font("freesansbold.ttf", size)
    TEXT = FONT.render(str(value), True, color)

    rect = TEXT.get_rect()
    #rect.center = x,y
    rect.x = x
    rect.y = y
    screen.blit(TEXT, rect)


def show_light():
    if len(last_ser) > 0:
        color = (int(last_ser[1]), int(last_ser[2]), int(last_ser[3]))
        pygame.draw.rect(screen, color, (screenwidth-120, 20, 100, 100))
    else:
        pygame.draw.rect(screen, (0, 0, 0), (screenwidth-120, 20, 100, 100))


def get_serial() -> str:

    a = s.readline().rstrip()
    return a.decode("utf-8").split(";")


def database_saver():

    if len(last_ser) > 0:
        if int(last_ser[4]) >= 1:
            database.append(str(round(float(last_ser[5])*100, 2)))
            x.append(float(input("Konsentrasjon: "))) # here
            y.append(round(float(last_ser[5])*100, 2)) # here
            with open("database.txt", "w") as f:
                f.write(str([database, x]))


def regression():

    if len(x) > 0 or len(y) > 0:
        m, b = np.polyfit(np.array(y), np.array(x), 1)
        return m, b
    else:
        return 0, 0


def show_regression(): #here

    plt.scatter(x[:-1], y[:-1])
    plt.scatter(x[len(x)-1:], y[len(y)-1:], edgecolors="g")
    print(f"Stigningstall: {round(stigningstall, 2)}, Konstantledd: {round(konstantledd, 2)}")
    plt.plot(np.array(x), stigningstall*np.array(x) + konstantledd)
    plt.plot(x, y, 'r')
    plt.show()


def show_database():

    new_database = []
    ctr = 0
    layer = 0
    for data in database:
        if ctr < 5:
            if len(new_database) < layer+1:
                new_database.append([])
            new_database[layer].append(data)
            
        else:
            layer += 1
            ctr = 0

        ctr += 1

    text(f"DATABASE ->", 25, (0, 150, 200), 30, 50)
    for pos, data in enumerate(new_database):
        text(f"{data}", 25, (0, 150, 200), 200, 50+(pos*30))

def show_serial():

    if len(last_ser) > 0:
        value = last_ser[0]
        value_ukjent = stigningstall*float(value) + konstantledd
        text(f"verdi  -> {value}", 30, (255, 255, 255), 740, 35)
        text(f"Ukjent -> {round(value_ukjent, 3)}", 30, (255, 255, 255), 740, 65)
    else:
        text(f"Ingen verdier", 30, (255, 255, 255), 740, 50)


def open_dataset():

    filename = askopenfilename(filetype=(("Dataset", ".txt"), ("All Files", "*.*")))
    with open(filename, "r") as f:
        global database
        data = ast.literal_eval(f.read())
        database = data[0]
        global x
        global y

        for x_ in data[1]:
            x.append(float(x_))

        for y_ in data[0]:
            y.append(float(y_))

FPSTicker = pygame.time.Clock()
running = True
while running:

    screen.fill((0,0,0))

    stigningstall, konstantledd = regression()
    print(stigningstall, konstantledd)

    last_ser = get_serial()
    last_ser[0] = str(round(float(last_ser[0])*100, 2))
    print(last_ser)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_regression()
            if event.key == pygame.K_o:
                open_dataset()

    show_light()
    show_serial()
    database_saver()
    show_database()

    FPSTicker.tick(60)
    pygame.display.flip()

pygame.quit()