""

































import numpy as np

from pyquaternion import Quaternion




from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

def generate_quaternion():
	q1 = Quaternion.random()
	q2 = Quaternion.random()
	while True:
		for q in Quaternion.intermediates(q1, q2, 20, include_endpoints=True):
			yield q

		q1 = q2
		q2 = Quaternion.random()

quaternion_generator = generate_quaternion()


fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1], projection='3d')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')



colors = ['r', 'g', 'b']


lines = sum([ax.plot([], [], [], c=c)
             for c in colors], [])

startpoints = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
endpoints = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


ax.set_xlim((-8, 8))
ax.set_ylim((-8, 8))
ax.set_zlim((-8, 8))


ax.view_init(30, 0)



def init():
    for line in lines:
        line.set_data([], [])
        line.set_3d_properties([])

    return lines


def animate(i):



    q = next(quaternion_generator)


    for line, start, end in zip(lines, startpoints, endpoints):

        start = q.rotate(start)
        end = q.rotate(end)

        line.set_data([start[0], end[0]], [start[1], end[1]])
        line.set_3d_properties([start[2], end[2]])





    fig.canvas.draw()
    return lines


anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=500, interval=30, blit=False)




plt.show()
