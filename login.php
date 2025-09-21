<?php
session_start();
require_once 'conectar.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Preparar a consulta SQL para buscar o usuário
    $sql = "SELECT * FROM usuarios WHERE username = :username LIMIT 1"; 
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':username', $username);
    $stmt->execute();

    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    // Verificar se o usuário existe e se a senha é válida (sem criptografia)
    if ($user && $password === $user['password']) { 
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        header('Location: config.php'); 
        exit;
    } else {
        // Se login falhar -> alerta + redireciona para tela inicial
        echo "<script>
                alert('Usuário ou senha inválidos.');
                window.location.href = 'login.html';
              </script>";
        exit;
    }
}
?>
