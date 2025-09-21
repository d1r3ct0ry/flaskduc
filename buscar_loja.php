<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$servername = "193.203.175.72"; // ou "localhost"
$username = "u928204666_sysdba"; // Seu usuário do banco
$password = "Fernandosa123"; // Sua senha
$dbname = "u928204666_MAINDUC"; // Nome do banco de dados
$port = "3306"; // Porta padrão do MySQL

// Cria a conexão
$conn = new mysqli($servername, $username, $password, $dbname, $port);

// Verifica a conexão
if ($conn->connect_error) {
    die(json_encode(["error" => "Conexão falhou: " . $conn->connect_error]));
}

$nome = isset($_GET['nome']) ? $_GET['nome'] : '';
$sql = "SELECT NOME FROM LOJAS WHERE NOME LIKE ? LIMIT 10";
$stmt = $conn->prepare($sql);

if (!$stmt) {
    die(json_encode(["error" => "Erro na preparação da consulta: " . $conn->error]));
}

$searchTerm = "%{$nome}%";
$stmt->bind_param("s", $searchTerm);
$stmt->execute();
$result = $stmt->get_result();

$lojas = [];
while ($row = $result->fetch_assoc()) {
    $lojas[] = $row;
}

echo json_encode($lojas);
$stmt->close();
$conn->close();
?>
