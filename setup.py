""                                                                                                        
    
                                          
   

                                         
from setuptools import setup, find_packages
                              
from codecs import open
import os

version = '0.0.0'
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION.txt')) as version_file:
    version = version_file.read().strip()

setup(
    name='pyquaternion',

                                                                              
                                                           
                                                                       
    version=version,

    description='A fully featured, pythonic library for representing and using quaternions.',
    long_description="A fully featured, pythonic library for quaternion representation, manipulation, 3D animation and geometry.",

                                  
    download_url='https://github.com/KieranWynn/pyquaternion/releases/latest',
    url='http://kieranwynn.github.io/pyquaternion/',

                    
    author='Kieran Wynn',
    author_email='KieranWynn@users.noreply.github.com',

                         
    license='MIT',

                                                                 
    classifiers=[
                                                       
                     
                    
                                 
        'Development Status :: 4 - Beta',

                                                   
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',


                                                                      
        'License :: OSI Approved :: MIT License',

                                                                             
                                                                           
        
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
        
        

                                       
    keywords=[
        'quaternion', 'math', 'maths', 'physics', 'orientation', 'pose', 'geometry', 'visualisation', 'animation'
    ],

                                                                        
                                             
    packages=['pyquaternion'],

                                                                             
           
                               

                                                                           
                                                                               
                             
                                                              
    install_requires=["numpy"],

                                                                   
                                                                      
                  
                                  
    extras_require={
        'dev': ["mkdocs"],
        'test': ["nose"]
    },

                                                                       
                                                                            
                                                 
    package_data={
    },

                                                                             
                                                             
                                                                                              
                                                                             
    data_files=[],

                                                                          
                                                                              
                                                                               
    entry_points={},

                                                  
    test_suite='nose.collector',

                                                 
    tests_require=['nose'],
)
