""

































from __future__ import absolute_import, division, print_function

from math import sqrt, pi, sin, cos, asin, acos, atan2, exp, log
from copy import deepcopy
import numpy as np


class Quaternion:
    ""









    def __init__(self, *args, **kwargs):
        ""






        s = len(args)
        if s == 0:

            if kwargs:

                if ("scalar" in kwargs) or ("vector" in kwargs):
                    scalar = kwargs.get("scalar", 0.0)
                    if scalar is None:
                        scalar = 0.0
                    else:
                        scalar = float(scalar)

                    vector = kwargs.get("vector", [])
                    vector = self._validate_number_sequence(vector, 3)

                    self.q = np.hstack((scalar, vector))
                elif ("real" in kwargs) or ("imaginary" in kwargs):
                    real = kwargs.get("real", 0.0)
                    if real is None:
                        real = 0.0
                    else:
                        real = float(real)

                    imaginary = kwargs.get("imaginary", [])
                    imaginary = self._validate_number_sequence(imaginary, 3)

                    self.q = np.hstack((real, imaginary))
                elif ("axis" in kwargs) or ("radians" in kwargs) or ("degrees" in kwargs) or ("angle" in kwargs):
                    try:
                        axis = self._validate_number_sequence(kwargs["axis"], 3)
                    except KeyError:
                        raise ValueError(
                            "A valid rotation 'axis' parameter must be provided to describe a meaningful rotation."
                        )
                    angle = kwargs.get('radians') or self.to_radians(kwargs.get('degrees')) or kwargs.get('angle') or 0.0
                    self.q = Quaternion._from_axis_angle(axis, angle).q
                elif "array" in kwargs:
                    self.q = self._validate_number_sequence(kwargs["array"], 4)
                elif "matrix" in kwargs:
                    optional_args = {key: kwargs[key] for key in kwargs if key in ['rtol', 'atol']}
                    self.q = Quaternion._from_matrix(kwargs["matrix"], **optional_args).q
                else:
                    keys = sorted(kwargs.keys())
                    elements = [kwargs[kw] for kw in keys]
                    if len(elements) == 1:
                        r = float(elements[0])
                        self.q = np.array([r, 0.0, 0.0, 0.0])
                    else:
                        self.q = self._validate_number_sequence(elements, 4)

            else:

                self.q = np.array([1.0, 0.0, 0.0, 0.0])
        elif s == 1:

            if isinstance(args[0], Quaternion):
                self.q = args[0].q
                return
            if args[0] is None:
                raise TypeError("Object cannot be initialised from {}".format(type(args[0])))
            try:
                r = float(args[0])
                self.q = np.array([r, 0.0, 0.0, 0.0])
                return
            except TypeError:
                pass

            self.q = self._validate_number_sequence(args[0], 4)
            return

        else:

            self.q = self._validate_number_sequence(args, 4)

    def __hash__(self):
        return hash(tuple(self.q))

    def _validate_number_sequence(self, seq, n):
        ""




        if seq is None:
            return np.zeros(n)
        if len(seq) == n:
            try:
                l = [float(e) for e in seq]
            except ValueError:
                raise ValueError("One or more elements in sequence <{!r}> cannot be interpreted as a real number".format(seq))
            else:
                return np.asarray(l)
        elif len(seq) == 0:
            return np.zeros(n)
        else:
            raise ValueError("Unexpected number of elements in sequence. Got: {}, Expected: {}.".format(len(seq), n))


    @classmethod
    def _from_matrix(cls, matrix, rtol=1e-05, atol=1e-08):
        ""





        try:
            shape = matrix.shape
        except AttributeError:
            raise TypeError("Invalid matrix type: Input must be a 3x3 or 4x4 numpy array or matrix")

        if shape == (3, 3):
            R = matrix
        elif shape == (4, 4):
            R = matrix[:-1][:,:-1]
        else:
            raise ValueError("Invalid matrix shape: Input must be a 3x3 or 4x4 numpy array or matrix")


        if not np.allclose(np.dot(R, R.conj().transpose()), np.eye(3), rtol=rtol, atol=atol):
            raise ValueError("Matrix must be orthogonal, i.e. its transpose should be its inverse")
        if not np.isclose(np.linalg.det(R), 1.0, rtol=rtol, atol=atol):
            raise ValueError("Matrix must be special orthogonal i.e. its determinant must be +1.0")

        def decomposition_method(matrix):
            ""


            x, y, z = 0, 1, 2
            K = np.array([
                [R[x, x]-R[y, y]-R[z, z],  R[y, x]+R[x, y],           R[z, x]+R[x, z],           R[y, z]-R[z, y]],
                [R[y, x]+R[x, y],          R[y, y]-R[x, x]-R[z, z],   R[z, y]+R[y, z],           R[z, x]-R[x, z]],
                [R[z, x]+R[x, z],          R[z, y]+R[y, z],           R[z, z]-R[x, x]-R[y, y],   R[x, y]-R[y, x]],
                [R[y, z]-R[z, y],          R[z, x]-R[x, z],           R[x, y]-R[y, x],           R[x, x]+R[y, y]+R[z, z]]
            ])
            K = K / 3.0

            e_vals, e_vecs = np.linalg.eig(K)
            print('Eigenvalues:', e_vals)
            print('Eigenvectors:', e_vecs)
            max_index = np.argmax(e_vals)
            principal_component = e_vecs[max_index]
            return principal_component

        def trace_method(matrix):
            ""







            m = matrix.conj().transpose()
            if m[2, 2] < 0:
                if m[0, 0] > m[1, 1]:
                    t = 1 + m[0, 0] - m[1, 1] - m[2, 2]
                    q = [m[1, 2]-m[2, 1],  t,  m[0, 1]+m[1, 0],  m[2, 0]+m[0, 2]]
                else:
                    t = 1 - m[0, 0] + m[1, 1] - m[2, 2]
                    q = [m[2, 0]-m[0, 2],  m[0, 1]+m[1, 0],  t,  m[1, 2]+m[2, 1]]
            else:
                if m[0, 0] < -m[1, 1]:
                    t = 1 - m[0, 0] - m[1, 1] + m[2, 2]
                    q = [m[0, 1]-m[1, 0],  m[2, 0]+m[0, 2],  m[1, 2]+m[2, 1],  t]
                else:
                    t = 1 + m[0, 0] + m[1, 1] + m[2, 2]
                    q = [t,  m[1, 2]-m[2, 1],  m[2, 0]-m[0, 2],  m[0, 1]-m[1, 0]]

            q = np.array(q).astype('float64')
            q *= 0.5 / sqrt(t)
            return q

        return cls(array=trace_method(R))


    @classmethod
    def _from_axis_angle(cls, axis, angle):
        ""








        mag_sq = np.dot(axis, axis)
        if mag_sq == 0.0:
            raise ZeroDivisionError("Provided rotation axis has no length")

        if (abs(1.0 - mag_sq) > 1e-12):
            axis = axis / sqrt(mag_sq)
        theta = angle / 2.0
        r = cos(theta)
        i = axis * sin(theta)

        return cls(r, i[0], i[1], i[2])

    @classmethod
    def random(cls):
        ""




        r1, r2, r3 = np.random.random(3)

        q1 = sqrt(1.0 - r1) * (sin(2 * pi * r2))
        q2 = sqrt(1.0 - r1) * (cos(2 * pi * r2))
        q3 = sqrt(r1)       * (sin(2 * pi * r3))
        q4 = sqrt(r1)       * (cos(2 * pi * r3))

        return cls(q1, q2, q3, q4)


    def __str__(self):
        ""

        return "{:.3f} {:+.3f}i {:+.3f}j {:+.3f}k".format(self.q[0], self.q[1], self.q[2], self.q[3])

    def __repr__(self):
        ""




        return "Quaternion({!r}, {!r}, {!r}, {!r})".format(self.q[0], self.q[1], self.q[2], self.q[3])

    def __format__(self, formatstr):
        ""




        if formatstr.strip() == '':
            formatstr = '+.3f'

        string = \
            "{:" + formatstr +"} "  + \
            "{:" + formatstr +"}i " + \
            "{:" + formatstr +"}j " + \
            "{:" + formatstr +"}k"
        return string.format(self.q[0], self.q[1], self.q[2], self.q[3])


    def __int__(self):
        ""





        return int(self.q[0])

    def __float__(self):
        ""




        return float(self.q[0])

    def __complex__(self):
        ""






        return complex(self.q[0], self.q[1])

    def __bool__(self):
        return not (self == Quaternion(0.0))

    def __nonzero__(self):
        return not (self == Quaternion(0.0))

    def __invert__(self):
        return (self == Quaternion(0.0))


    def __eq__(self, other):
        ""


        if isinstance(other, Quaternion):
            r_tol = 1.0e-13
            a_tol = 1.0e-14
            try:
                isEqual = np.allclose(self.q, other.q, rtol=r_tol, atol=a_tol)
            except AttributeError:
                raise AttributeError("Error in internal quaternion representation means it cannot be compared like a numpy array.")
            return isEqual
        return self.__eq__(self.__class__(other))


    def __neg__(self):
        return self.__class__(array= -self.q)


    def __abs__(self):
        return self.norm


    def __add__(self, other):
        if isinstance(other, Quaternion):
            return self.__class__(array=self.q + other.q)
        return self + self.__class__(other)

    def __iadd__(self, other):
        return self + other

    def __radd__(self, other):
        return self + other


    def __sub__(self, other):
        return self + (-other)

    def __isub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return -(self - other)


    def __mul__(self, other):
        if isinstance(other, Quaternion):
            return self.__class__(array=np.dot(self._q_matrix(), other.q))
        return self * self.__class__(other)

    def __imul__(self, other):
        return self * other

    def __rmul__(self, other):
        return self.__class__(other) * self

    def __matmul__(self, other):
        if isinstance(other, Quaternion):
            return self.q.__matmul__(other.q)
        return self.__matmul__(self.__class__(other))

    def __imatmul__(self, other):
        return self.__matmul__(other)

    def __rmatmul__(self, other):
        return self.__class__(other).__matmul__(self)


    def __div__(self, other):
        if isinstance(other, Quaternion):
            if other == self.__class__(0.0):
                raise ZeroDivisionError("Quaternion divisor must be non-zero")
            return self * other.inverse
        return self.__div__(self.__class__(other))

    def __idiv__(self, other):
        return self.__div__(other)

    def __rdiv__(self, other):
        return self.__class__(other) * self.inverse

    def __truediv__(self, other):
        return self.__div__(other)

    def __itruediv__(self, other):
        return self.__idiv__(other)

    def __rtruediv__(self, other):
        return self.__rdiv__(other)


    def __pow__(self, exponent):

        exponent = float(exponent)
        norm = self.norm
        if norm > 0.0:
            try:
                n, theta = self.polar_decomposition
            except ZeroDivisionError:

                return Quaternion(scalar=self.scalar ** exponent)
            return (self.norm ** exponent) * Quaternion(scalar=cos(exponent * theta), vector=(n * sin(exponent * theta)))
        return Quaternion(self)

    def __ipow__(self, other):
        return self ** other

    def __rpow__(self, other):
        return other ** float(self)


    def _vector_conjugate(self):
        return np.hstack((self.q[0], -self.q[1:4]))

    def _sum_of_squares(self):
        return np.dot(self.q, self.q)

    @property
    def conjugate(self):
        ""






        return self.__class__(scalar=self.scalar, vector=-self.vector)

    @property
    def inverse(self):
        ""






        ss = self._sum_of_squares()
        if ss > 0:
            return self.__class__(array=(self._vector_conjugate() / ss))
        else:
            raise ZeroDivisionError("a zero quaternion (0 + 0i + 0j + 0k) cannot be inverted")

    @property
    def norm(self):
        ""







        mag_squared = self._sum_of_squares()
        return sqrt(mag_squared)

    @property
    def magnitude(self):
        return self.norm

    def _normalise(self):
        ""


        if not self.is_unit():
            n = self.norm
            if n > 0:
                self.q = self.q / n

    def _fast_normalise(self):
        ""




        if not self.is_unit():
            mag_squared = np.dot(self.q, self.q)
            if (mag_squared == 0):
                return
            if (abs(1.0 - mag_squared) < 2.107342e-08):
                mag =  ((1.0 + mag_squared) / 2.0)
            else:
                mag =  sqrt(mag_squared)

            self.q = self.q / mag

    @property
    def normalised(self):
        ""






        q = Quaternion(self)
        q._normalise()
        return q

    @property
    def polar_unit_vector(self):
        vector_length = np.linalg.norm(self.vector)
        if vector_length <= 0.0:
            raise ZeroDivisionError('Quaternion is pure real and does not have a unique unit vector')
        return self.vector / vector_length

    @property
    def polar_angle(self):
         return acos(self.scalar / self.norm)

    @property
    def polar_decomposition(self):
        ""






        return self.polar_unit_vector, self.polar_angle

    @property
    def unit(self):
        return self.normalised

    def is_unit(self, tolerance=1e-14):
        ""







        return abs(1.0 - self._sum_of_squares()) < tolerance

    def _q_matrix(self):
        ""

        return np.array([
            [self.q[0], -self.q[1], -self.q[2], -self.q[3]],
            [self.q[1],  self.q[0], -self.q[3],  self.q[2]],
            [self.q[2],  self.q[3],  self.q[0], -self.q[1]],
            [self.q[3], -self.q[2],  self.q[1],  self.q[0]]])

    def _q_bar_matrix(self):
        ""

        return np.array([
            [self.q[0], -self.q[1], -self.q[2], -self.q[3]],
            [self.q[1],  self.q[0],  self.q[3], -self.q[2]],
            [self.q[2], -self.q[3],  self.q[0],  self.q[1]],
            [self.q[3],  self.q[2], -self.q[1],  self.q[0]]])

    def _rotate_quaternion(self, q):
        ""







        self._normalise()
        return self * q * self.conjugate

    def rotate(self, vector):
        ""















        if isinstance(vector, Quaternion):
            return self._rotate_quaternion(vector)
        q = Quaternion(vector=vector)
        a = self._rotate_quaternion(q).vector
        if isinstance(vector, list):
            l = [x for x in a]
            return l
        elif isinstance(vector, tuple):
            l = [x for x in a]
            return tuple(l)
        else:
            return a

    @classmethod
    def exp(cls, q):
        ""












        tolerance = 1e-17
        v_norm = np.linalg.norm(q.vector)
        vec = q.vector
        if v_norm > tolerance:
            vec = vec / v_norm
        magnitude = exp(q.scalar)
        return Quaternion(scalar = magnitude * cos(v_norm), vector = magnitude * sin(v_norm) * vec)

    @classmethod
    def log(cls, q):
        ""












        v_norm = np.linalg.norm(q.vector)
        q_norm = q.norm
        tolerance = 1e-17
        if q_norm < tolerance:

            return Quaternion(scalar=-float('inf'), vector=float('nan')*q.vector)
        if v_norm < tolerance:

            return Quaternion(scalar=log(q_norm), vector=[0, 0, 0])
        vec = q.vector / v_norm
        return Quaternion(scalar=log(q_norm), vector=acos(q.scalar/q_norm)*vec)

    @classmethod
    def exp_map(cls, q, eta):
        ""

















        return q * Quaternion.exp(eta)

    @classmethod
    def sym_exp_map(cls, q, eta):
        ""
















        sqrt_q = q ** 0.5
        return sqrt_q * Quaternion.exp(eta) * sqrt_q

    @classmethod
    def log_map(cls, q, p):
        ""












        return Quaternion.log(q.inverse * p)

    @classmethod
    def sym_log_map(cls, q, p):
        ""














        inv_sqrt_q = (q ** (-0.5))
        return Quaternion.log(inv_sqrt_q * p * inv_sqrt_q)

    @classmethod
    def absolute_distance(cls, q0, q1):
        ""
















        q0_minus_q1 = q0 - q1
        q0_plus_q1  = q0 + q1
        d_minus = q0_minus_q1.norm
        d_plus  = q0_plus_q1.norm
        if d_minus < d_plus:
            return d_minus
        else:
            return d_plus

    @classmethod
    def distance(cls, q0, q1):
        ""
















        q = Quaternion.log_map(q0, q1)
        return q.norm

    @classmethod
    def sym_distance(cls, q0, q1):
        ""



















        q = Quaternion.sym_log_map(q0, q1)
        return q.norm

    @classmethod
    def slerp(cls, q0, q1, amount=0.5):
        ""























        q0._fast_normalise()
        q1._fast_normalise()
        amount = np.clip(amount, 0, 1)

        dot = np.dot(q0.q, q1.q)




        if dot < 0.0:
            q0.q = -q0.q
            dot = -dot


        if dot > 0.9995:
            qr = Quaternion(q0.q + amount * (q1.q - q0.q))
            qr._fast_normalise()
            return qr

        theta_0 = np.arccos(dot)
        sin_theta_0 = np.sin(theta_0)

        theta = theta_0 * amount
        sin_theta = np.sin(theta)

        s0 = np.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0
        qr = Quaternion((s0 * q0.q) + (s1 * q1.q))
        qr._fast_normalise()
        return qr

    @classmethod
    def intermediates(cls, q0, q1, n, include_endpoints=False):
        ""






















        step_size = 1.0 / (n + 1)
        if include_endpoints:
            steps = [i * step_size for i in range(0, n + 2)]
        else:
            steps = [i * step_size for i in range(1, n + 1)]
        for step in steps:
            yield cls.slerp(q0, q1, step)

    def derivative(self, rate):
        ""







        rate = self._validate_number_sequence(rate, 3)
        return 0.5 * self * Quaternion(vector=rate)

    def integrate(self, rate, timestep):
        ""

















        self._fast_normalise()
        rate = self._validate_number_sequence(rate, 3)

        rotation_vector = rate * timestep
        rotation_norm = np.linalg.norm(rotation_vector)
        if rotation_norm > 0:
            axis = rotation_vector / rotation_norm
            angle = rotation_norm
            q2 = Quaternion(axis=axis, angle=angle)
            self.q = (self * q2).q
            self._fast_normalise()


    @property
    def rotation_matrix(self):
        ""








        self._normalise()
        product_matrix = np.dot(self._q_matrix(), self._q_bar_matrix().conj().transpose())
        return product_matrix[1:][:, 1:]

    @property
    def transformation_matrix(self):
        ""







        t = np.array([[0.0], [0.0], [0.0]])
        Rt = np.hstack([self.rotation_matrix, t])
        return np.vstack([Rt, np.array([0.0, 0.0, 0.0, 1.0])])

    @property
    def yaw_pitch_roll(self):
        ""












        self._normalise()
        yaw = np.arctan2(2 * (self.q[0] * self.q[3] - self.q[1] * self.q[2]),
            1 - 2 * (self.q[2] ** 2 + self.q[3] ** 2))
        pitch = np.arcsin(2 * (self.q[0] * self.q[2] + self.q[3] * self.q[1]))
        roll = np.arctan2(2 * (self.q[0] * self.q[1] - self.q[2] * self.q[3]),
            1 - 2 * (self.q[1] ** 2 + self.q[2] ** 2))

        return yaw, pitch, roll

    def _wrap_angle(self, theta):
        ""



        result = ((theta + pi) % (2 * pi)) - pi
        if result == -pi:
            result = pi
        return result

    def get_axis(self, undefined=np.zeros(3)):
        ""

















        tolerance = 1e-17
        self._normalise()
        norm = np.linalg.norm(self.vector)
        if norm < tolerance:

            return undefined
        else:
            return self.vector / norm

    @property
    def axis(self):
        return self.get_axis()

    @property
    def angle(self):
        ""

















        self._normalise()
        norm = np.linalg.norm(self.vector)
        return self._wrap_angle(2.0 * atan2(norm, self.scalar))

    @property
    def degrees(self):
        return self.to_degrees(self.angle)

    @property
    def radians(self):
        return self.angle

    @property
    def scalar(self):
        ""




        return self.q[0]

    @property
    def vector(self):
        ""




        return self.q[1:4]

    @property
    def real(self):
        return self.scalar

    @property
    def imaginary(self):
        return self.vector

    @property
    def w(self):
        return self.q[0]

    @property
    def x(self):
        return self.q[1]

    @property
    def y(self):
        return self.q[2]

    @property
    def z(self):
        return self.q[3]

    @property
    def elements(self):
        ""




        return self.q

    def __getitem__(self, index):
        index = int(index)
        return self.q[index]

    def __setitem__(self, index, value):
        index = int(index)
        self.q[index] = float(value)

    def __copy__(self):
        result = self.__class__(self.q)
        return result

    def __deepcopy__(self, memo):
        result = self.__class__(deepcopy(self.q, memo))
        memo[id(self)] = result
        return result

    @staticmethod
    def to_degrees(angle_rad):
        if angle_rad is not None:
            return float(angle_rad) / pi * 180.0

    @staticmethod
    def to_radians(angle_deg):
        if angle_deg is not None:
            return float(angle_deg) / 180.0 * pi
