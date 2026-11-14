"""Install the optional, mock-only controller testbed."""

from glob import glob
from setuptools import setup


setup(
    name='carrier_controller_testbed', version='0.1.0',
    packages=['carrier_controller_testbed'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/carrier_controller_testbed']),
        ('share/carrier_controller_testbed', ['package.xml']),
        ('share/carrier_controller_testbed/launch', glob('launch/*.launch.py')),
        ('share/carrier_controller_testbed/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='CAM-BOT contributors', maintainer_email='shanmukha@example.com',
    description='Isolated ros2_control mock UR5 protocol testbed; no physical actuation.',
    license='Apache-2.0',
)
