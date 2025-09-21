<?php
session_start();
require_once 'conectar.php'; // Certifique-se de que a conexão com o banco de dados está correta

// Verificar se o usuário está logado
if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit;
}

// Obter o nome do usuário logado (ajuste conforme necessário)
$userName = $_SESSION['user_name'] ?? 'Usuário';

// Obter o estado atual do campo 'prazo' da tabela CONFIG
$sql = "SELECT prazo FROM CONFIG LIMIT 1";
$stmt = $pdo->prepare($sql);
$stmt->execute();
$config = $stmt->fetch(PDO::FETCH_ASSOC);

// Verificar se o formulário foi enviado para atualizar a configuração
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Alternar o estado do booleano entre 0 e 1
    $newState = ($config['prazo'] == 1) ? 0 : 1; // Se 'prazo' for 1, muda para 0, senão, para 1

    // Atualizar o valor no banco de dados
    $updateSql = "UPDATE CONFIG SET prazo = :newState WHERE 1"; // Aqui estamos atualizando a primeira linha da tabela
    $updateStmt = $pdo->prepare($updateSql);
    $updateStmt->bindParam(':newState', $newState, PDO::PARAM_INT);
    $updateStmt->execute();

    // Atualizar o estado local para refletir a mudança imediatamente na interface
    $config['prazo'] = $newState;
}

// Função de logout
if (isset($_GET['logout'])) {
    session_destroy(); // Destroi todas as sessões
    header('Location: login.php'); // Redireciona para a página de login
    exit;
}
?>

<?php
$arquivo = 'dadosFrete.js';

// Salvar alterações
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $texto = $_POST['conteudo'] ?? '';
    file_put_contents($arquivo, $texto);
    echo "<p>Alterações salvas com sucesso!</p>";
}

// Ler conteúdo atual
$conteudo = file_get_contents($arquivo);
?>

<?php
$arquivo = 'dadosFrete.js';
$backupDir = 'backups';

// Criar pasta de backup se não existir
if (!is_dir($backupDir)) {
    mkdir($backupDir, 0755, true);
}

// Salvar alterações
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $texto = $_POST['conteudo'] ?? '';
    // Backup automático dentro da pasta 'backups'
    $backup = $backupDir . '/dadosFrete_backup_' . date('Ymd_His') . '.js';
    copy($arquivo, $backup);
    file_put_contents($arquivo, $texto);
    $mensagem = "Alterações salvas com sucesso! Backup criado: $backup";
}

// Ler conteúdo atual
$conteudo = file_get_contents($arquivo);
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Editar Tabela de Frete</title>
  <!-- Bootstrap 5 CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-5">
    <h1 class="mb-4 text-center">Editar Tabela de Frete</h1>

    <?php if (!empty($mensagem)) : ?>
      <div class="alert alert-success"><?php echo htmlspecialchars($mensagem); ?></div>
    <?php endif; ?>

    <form method="post">
      <div class="mb-3">
        <textarea name="conteudo" class="form-control" style="height:500px; font-family: monospace;"><?php echo htmlspecialchars($conteudo); ?></textarea>
      </div>
      <div class="d-flex justify-content-center">
        <button type="submit" class="btn btn-primary btn-lg">💾 Salvar Alterações</button>
      </div>
    </form>
  </div>

  <!-- Bootstrap JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
