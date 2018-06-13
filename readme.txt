prerequisites

Django 가상환경 설정(mac 기준)
pip3 install virtualenv
virtualenv ~/eb-virt
source ~/eb-virt/bin/activate

requirements.txt 설치
pip install -r requirements.txt

개발 후 deploy 과정
git add .
git commit
eb deploy --staged

확인
eb open
