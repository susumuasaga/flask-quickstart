# Usando Cloud Foundry para Implantar uma Aplicação Python

Edson Susumu Asaga
2020-11-28

## Introdução

*Cloud Foundry* é uma plataforma de aplicações baseada em contêineres, multinuvem de fonte aberta.

O objetivo desde artigo é mostrar como ela pode ser usada para implantar uma aplicação Python na nuvem privada do Bradesco e identificar deficiências na configuração atualmente instalada.

## Login e Target

Ao usar Cloud Foundry, a primeira coisa que é necessário fazer é se logar numa instância Cloud Foundry. Para se logar, executar o seguinte comando:
```bash
cf login -a api.system.pasnext.ti.bradesco.com.br -u m236828 --skip-ssl-validation
```

Vamos dissecar o comando `login`:

* A opção `-a` permite especificar o endpoint da API da instância Cloud Foundry.
* A opção `-u` permite especificar o username para a instância Cloud Foundry.
* Propositalmente, omitimos a opção `-p` para fornecer a senha (no caso `Br@desc0`) na linha de comando. Esta opção existe, mas foi projetada para automação. 

Se o login for feito com êxito, deve ser mostrado uma saída semelhante a abaixo:
```
API endpoint: api.system.pasnext.ti.bradesco.com.br

Password>
Authenticating...
OK

Targeted org next.bradesco.com.br

Targeted space dev


Cloud Foundry API version 2.120.0 requires CLI version 6.23.0.  You are currently on version 6.21.1+6fd3c9f. To upgrade your CLI, please visit: https://github.com/cloudfoundry/cli#downloads


API endpoint:   https://api.system.pasnext.ti.bradesco.com.br (API version: 2.120.0)
User:           m236828
Org:            next.bradesco.com.br
Space:          dev
```

Observe o aviso para atualizar a versão do CLI de 6.21.1 para 6.23.0, mas isso não está impedindo a execução com êxito do comando.

## Configurar a Aplicação Python

### A Aplicação

Não tem nada de especial sobre a aplicação que vamos implantar. É uma simples aplicação “Hello world” escrita para o propósito de treinamento, está host `al-vl-vb-408` no diretório `/data/workdir/next/flask-quickstart`.

Cloud Foundry usa automaticamente o Python buildpack quando detecta um arquivo `requirements.txt`ou `setup.py` no diretório raiz do projeto.

### Especificar a Versão Python

Especificamos a versão de execução do Python o incluindo em um arquivo `runtime.txt`

```
python-3.6.x
```

Na nossa aplicação, usamos f-strings que foram disponibilizadas na versão 3.6.

### Especificar o Comando Inicial

O Python buildpack não gera um comando inicial padrão para as aplicações.

Especificamos o comando inicial da aplicação em um arquivo `Procfile` 
```
web: python hello.py
```

### Executar o Servidor Web

Por padrão, o Python buildpack espera que a aplicação Python escute o porto 8080. A variável de ambiente `PORT` é usada para passar outro porto.

```python
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run('0.0.0.0', port)
```

### Fornecer Dependências da Aplicação

Como estamos implantando em um ambiente que está desconectado da Internet, aplicação deve fornecer suas dependências.

Para o Python buildpack, devemos baixar as dependências previamente em uma máquina conectada usando `pip`:

```bash
cd /data/workdir/next/flask-quickstart
mkdir -p vendor
pip download -r requirements.txt -d vendor
```

O buildpack instala as dependências diretamente do diretório `vendor`.

Alternativamente também poderia ser usado o repositório privado Nexus para fazer a instalação de dependências.

## Implantar a Aplicação

A implantação da aplicação é realizada dando um `cf push` (precisa estar no diretório `flask-quickstart`): 

```bash
cf push flask-quickstart -b python_buildpack -m 64M
```

Vamos dissecar o comando `push`:

* `flask-quickstart` é o nome da aplicação em Cloud Foundry.
* `-b python_buildpack` diz a Cloud Foundry usar o Python buildpack para implantar a aplicação. Esse parâmetro é opcional, poderíamos deixar Cloud Foundry decidir automaticamente qual buildpack usar, mas especificando via `-b` é um pouco mais rápido.
* `m 64M` diz a Cloud Foundry alocar 64MB de memória para o contêiner que executa a aplicação.

Se tudo der certo, devemos ver a saída da aplicação sendo executada:

```
Downloading python_buildpack...
Downloaded python_buildpack
Cell cb55a007-a26e-4409-9bd3-67215d456b0b creating container for instance 689488e7-215e-48ab-aeba-dc2b19b041e2
Cell cb55a007-a26e-4409-9bd3-67215d456b0b successfully created container for instance 689488e7-215e-48ab-aeba-dc2b19b041e2
Downloading build artifacts cache...
Downloaded build artifacts cache (217B)
Downloading app package...
Downloaded app package (684.4K)
-----> Python Buildpack version 1.6.36
       **WARNING**
       !! !!
       This application is being deployed on cflinuxfs2 which is being deprecated in April, 2019.
       Please migrate this application to cflinuxfs3.
       For more information about changing the stack, see https://docs.cloudfoundry.org/devguide/deploy-apps/stacks.html
       !! !!
-----> Supplying Python
-----> Installing python 3.6.9
       Copy [/tmp/buildpacks/181ce3444df7af68dc0051682db065f1/dependencies/c5808876fc41d21559c197631a44cfe6/python-3.6.9-linux-x64-cflinuxfs2-4398685f.tgz]
-----> Installing pip-pop 0.1.3
       Copy [/tmp/buildpacks/181ce3444df7af68dc0051682db065f1/dependencies/859523d4d2137906b68eb4c8951d56b3/pip-pop-0.1.3-fc106ef6.tar.gz]
-----> Running Pip Install
       Using the pip --no-build-isolation flag since it is available
       Looking in links: file:///tmp/app/vendor
       Collecting flask (from -r /tmp/app/requirements.txt (line 1))
       Collecting cfenv (from -r /tmp/app/requirements.txt (line 2))
       Collecting Werkzeug>=0.15 (from flask->-r /tmp/app/requirements.txt (line 1))
       Collecting click>=5.1 (from flask->-r /tmp/app/requirements.txt (line 1))
       Collecting Jinja2>=2.10.1 (from flask->-r /tmp/app/requirements.txt (line 1))
       Collecting itsdangerous>=0.24 (from flask->-r /tmp/app/requirements.txt (line 1))
       Collecting furl>=0.4.8 (from cfenv->-r /tmp/app/requirements.txt (line 2))
       Collecting MarkupSafe>=0.23 (from Jinja2>=2.10.1->flask->-r /tmp/app/requirements.txt (line 1))
       Collecting six>=1.8.0 (from furl>=0.4.8->cfenv->-r /tmp/app/requirements.txt (line 2))
       Collecting orderedmultidict>=1.0.1 (from furl>=0.4.8->cfenv->-r /tmp/app/requirements.txt (line 2))
       Installing collected packages: Werkzeug, click, MarkupSafe, Jinja2, itsdangerous, flask, six, orderedmultidict, furl, cfenv
         The script flask is installed in '/tmp/contents076468498/deps/0/python/bin' which is not on PATH.
         Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
       Successfully installed Jinja2-2.11.2 MarkupSafe-1.1.1 Werkzeug-1.0.1 cfenv-0.5.3 click-7.1.2 flask-1.1.2 furl-2.1.0 itsdangerous-1.1.0 orderedmultidict-1.0.1 six-1.15.0
Exit status 0
Uploading droplet, build artifacts cache...
Uploading droplet...
Uploading build artifacts cache...
Uploaded build artifacts cache (224B)
Uploaded droplet (49M)
Uploading complete
Cell cb55a007-a26e-4409-9bd3-67215d456b0b stopping instance 689488e7-215e-48ab-aeba-dc2b19b041e2
Cell cb55a007-a26e-4409-9bd3-67215d456b0b destroying container for instance 689488e7-215e-48ab-aeba-dc2b19b041e2
Cell cb55a007-a26e-4409-9bd3-67215d456b0b successfully destroyed container for instance 689488e7-215e-48ab-aeba-dc2b19b041e2

0 of 1 instances running, 1 starting
1 of 1 instances running

App started


OK

App flask-quickstart was started using this command `python hello.py`

Showing health and status for app flask-quickstart in org next.bradesco.com.br / space dev as m236828...
OK

requested state: started
instances: 1/1
usage: 64M x 1 instances
urls: flask-quickstart.apps.pasnext.ti.bradesco.com.br
last uploaded: Mon Nov 30 19:40:05 UTC 2020
stack: cflinuxfs2
buildpack: python_buildpack

     state     since                    cpu    memory       disk           details
#0   running   2020-11-30 04:40:48 PM   0.0%   18M of 64M   175.9M of 1G
```

### Atualização do Python Buildpack pelo Operador

A saída acima mostra o aviso de que a aplicação está sendo implantada na pilha  `cflinuxfs2`, que foi descontinuada em abril de 2019 e pede para migrar para a pilha  `cflinuxfs3`. De fato, o Python buildpack foi configurado no nosso Cloud Foundry nas duas pilhas, mas a `cflinuxfs2` está em posição mais elevada, por isso acaba sendo usada ao invés da `cflinuxfs3`. Isso pode ser corrigido pelo operador, mas por meio do seguinte comando, que apaga o Python buildpack mais antigo. Essa operação só pode ser realizada por um operador e não por um desenvolvedor.

```bash
cf delete-buildpack python_buildpack
```

### Testar usando Postman

A aplicação tem uma interface de usuário que mostra alguns detalhes sobre a aplicação. O URL da aplicação está mostrado na saída acima: `flask-quickstart.apps.pasnext.ti.bradesco.com.br`. Mas essa URL está registrada no DNS interno, assim o DNS externo usado pelo Postman não vai resolver o endereço IP do servidor de Cloud Foundry: `10.195.171.200`. Então temos que usar o endereço de IP para fazer a requisição HTTP e adicionar um header `Host` com valor `flask-quickstart.apps.pasnext.ti.bradesco.com.br` para o servidor de Cloud Foundry saber para qual aplicação deve ser roteada a requisição.

Feitas as configurações indicadas, podemos testar a aplicação usando Postman, obtendo a tela abaixo:

![Flask-quickstart teste1](C:\Users\m236828\flask-quickstart\postman1.png) 

Observamos que endereço da instância, `10.195.171.184:61002`, é diferente do endereço do servidor Cloud Foundry, este é sempre fixo e tem nome registrado no DNS interno, enquanto aquele é variável.