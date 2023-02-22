from setuptools import setup

setup(name='teamviewer_iot_python_sdk',
      version='1.1.0',
      description='Iot client to put data in TeamViewer Iot.',
      url='',
      author='TeamViewer',
      author_email='@TeamViewer.com',
      license='MIT',
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
      packages=['TeamViewerIoTPythonSDK', 'docs', 'examples'],
      package_data={'docs': ['html/*.html', 'html/*.js', 'html/*.inv', 'html/_static/*']},
      include_package_data=True,
      install_requires=[
          'setuptools>=18.5',
          'cryptography',
          'paho-mqtt==1.3.1'
      ],
      zip_safe=False)

