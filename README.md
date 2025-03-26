## E-Mail Header Analyzer (MHA) with IPv6 Support
![mha](https://cloud.githubusercontent.com/assets/1170490/18221866/b7b362d6-718e-11e6-9fa0-2e7f8bc2b9d7.png)


## What is E-Mail header analyzer (MHA):
E-Mail header analyzer is a tool written in [flask](http://flask.pocoo.org/) for parsing email headers and converting them to a human readable format and it also can:
* Identify hop delays.
* Identify the source of the email.
* Identify hop country.


## MHA is an alternative for the following:
| Name | Dev | Issues |
| ---- | --- | ----- |
| [MessageHeader](https://toolbox.googleapps.com/apps/messageheader/) | Google | Not showing all the hops. |
| [EmailHeaders](https://mxtoolbox.com/Public/Tools/EmailHeaders.aspx) | Mxtoolbox | Not accurate and slow. |
| [Message Header Analyzer](https://testconnectivity.microsoft.com/MHA/Pages/mha.aspx) | Microsoft | Broken UI. |


## Installation
Install system dependencies:
```
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install virtualenv
```
Create a Python3 virtual environment and activate it:
```
virtualenv virt
source virt/bin/activate
```
Clone the GitHub repo:
```
git clone https://github.com/lnxg33k/email-header-analyzer.git
```
Install Python dependencies:
```
cd MHA
pip3 install -r requirements.txt
```
Run the development server:
`python3 server.py -d`

You can change the bind address or port by specifying the appropriate options:
`python3 server.py -b 0.0.0.0 -p 8080`

Everything should go well, now visit [http://localhost:8080](http://localhost:8080).

## Docker

A `Dockerfile` is provided if you wish to build a docker image.

```
docker build -t mha:latest .
```

You can then run a container with:

```
docker run -d -p 8080:8080 mha:latest
```

### Docker-Compose

A `docker-compose` file is provided if you wish to use docker-compose.

Clone the GitHub repo:
```
git clone https://github.com/lnxg33k/email-header-analyzer.git
cd email-header-analyzer
```

Let docker-compose do the work.
```
docker-compose up -d
```

Stop the container.
```
docker-compose down
```

HowTo enable debugging. Add in the docker `docker-compose.yml` file the line
```yaml
command: --debug
```
