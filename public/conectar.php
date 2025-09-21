<?php
$host = '127.0.0.1';  // Ou o endereço IP ou domínio do servidor MySQL se não for local
$port = '3306'; // Porta padrão do MySQL
$dbname = 'u928204666_MAINDUC';  // Nome do banco de dados que você deseja acessar
$username = 'u928204666_sysdba';  // Usuário MySQL
$password = 'DucEntregas123';  // Senha do usuário

try {
    // Conectar ao banco de dados, incluindo a porta e o charset UTF-8
    $pdo = new PDO("mysql:host=$host;port=$port;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);  // Definir modo de erro
} catch (PDOException $e) {
    die("Erro na conexão: " . $e->getMessage());
}
?>
