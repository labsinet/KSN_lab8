# Лабораторна робота №8 — Vagrantfile
# Заповніть файл відповідно до вашого варіанту (див. variant.txt і README.md).

Vagrant.configure("2") do |config|
  # TODO: вкажіть box свого варіанту (наприклад, "bento/ubuntu-22.04")
  config.vm.box = "CHANGE_ME/box"

  # TODO: задайте ім'я хоста (наприклад, "lab8-vm")
  # config.vm.hostname = "lab8-vm"

  # TODO: прокиньте порт 80 гостя на порт 8080 хоста
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  config.vm.synced_folder ".", "/vagrant"

  # TODO: ресурси ВМ (щонайменше 1024 МБ ОЗУ та 1 CPU)
  # config.vm.provider "virtualbox" do |vb|
  #   vb.name   = "lab8-vm"
  #   vb.memory = 1024
  #   vb.cpus   = 1
  # end

  # TODO: provisioner, що встановлює вебсервер (nginx / apache2 / httpd)
  # config.vm.provision "shell", inline: <<-SHELL
  #   ...
  # SHELL
end
