<todo>

[6.25]
1. https + single instance without load balancer 
2. control memory allocation by freeing
3. faster search
4. image cache

<what I touched>

[6.25]
1. locale
2. memory allocation failure in ec2 + how to deal with it(reboot?)

<prerequisites>

pip3 install virtualenv
virtualenv ~/eb-virt
source ~/eb-virt/bin/activate

pip install -r requirements.txt

git add .
git commit
eb deploy --staged

eb open


