# Project: Tortoise
This project was done in the context of the Artificial Intelligent class in second year at ENSICAEN

This project implements reinforcement learning in python applied to a tortoise game.
The tortoise has learned to eat lettuce and avoid the dog to survive.

![Screenshot from 2024-09-11 21-12-16](https://github.com/user-attachments/assets/6894830a-d1bd-4a21-ac5a-b1289231a0d9)

## Project credits
Students:  
- Paul NGUYEN  
- Cécile LU

Course Professor and lab supervisor:  
- Prof. Regis Clouard

## Random agent

~~~
./tortoise.py
python tortoise.py -a RandomBrain -w 15 -s 40
~~~

## ReflexAgent

~~~
./tortoise.py -a ReflexBrain -w 15 -s 30
~~~

## Exercise: Rational Agent"

~~~
./tortoise.py -a RationalBrain -w 15 -s 30

~~~
### multiple quiet executions
~~~
./runs.py -a RationalBrain -w 15 -n 10
~~~

