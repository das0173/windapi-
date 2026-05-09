"""Translate WindsurfPoolAPI dashboard from Chinese to PT-BR."""
import re

INPUT = r"c:\Users\Daniel\Downloads\windsurf-automation\WindsurfPoolAPI\src\dashboard\index.html"

# Chinese -> Portuguese (BR) translation map
translations = {
    # Page title
    "WindsurfPoolAPI 控制台": "WindsurfPoolAPI - Painel de Controle",
    # Sidebar brand
    "API de piscina de vento": "Windsurf Pool API",
    "Console de gerenciamento": "Painel de Gerenciamento",
    # Nav groups
    ">概览<": ">Visão Geral<",
    ">账号<": ">Contas<",
    ">系统<": ">Sistema<",
    # Nav items
    ">仪表盘<": ">Painel<",
    ">统计分析<": ">Estatísticas<",
    ">登录取号<": ">Login / Obter Token<",
    ">账号管理<": ">Gerenciamento de Contas<",
    ">异常监测<": ">Monitoramento de Anomalias<",
    ">模型控制<": ">Controle de Modelos<",
    ">代理配置<": ">Configuração de Proxy<",
    ">运行日志<": ">Logs de Execução<",
    ">实验性功能<": ">Recursos Experimentais<",
    ">Chaves de API<": ">Chaves de API<",
    # Login
    "请输入密码访问控制台": "Digite a senha para acessar o painel",
    "控制台密码": "Senha do Painel",
    "进入控制台": "Entrar no Painel",
    "密码错误，请重试": "Senha incorreta, tente novamente",
    # Overview page
    "系统概览": "Visão Geral do Sistema",
    "实时监控服务状态和运行指标": "Monitoramento em tempo real do status e métricas",
    "运行时间": "Tempo Online",
    "账号池": "Pool de Contas",
    "活跃": "Ativas",
    "错误": "Erros",
    "总请求": "Total de Requisições",
    "成功率": "Taxa de Sucesso",
    "缓存命中": "Cache Hit",
    "语言服务器": "Language Server",
    "运行中": "Rodando",
    "已停止": "Parado",
    "LS 实例池": "Pool de Instâncias LS",
    "刷新": "Atualizar",
    # Stats page
    "统计分析": "Estatísticas",
    "请求统计、账号用量和性能指标的详细分析": "Análise detalhada de requisições, uso de contas e métricas de desempenho",
    "请求总量": "Total de Requisições",
    "成功请求": "Requisições com Sucesso",
    "失败请求": "Requisições com Falha",
    "平均延迟": "Latência Média",
    "每日请求分布": "Distribuição Diária de Requisições",
    "请求详情": "Detalhes das Requisições",
    "最近的请求记录": "Registros recentes de requisições",
    "账号用量排行": "Ranking de Uso por Conta",
    "模型用量排行": "Ranking de Uso por Modelo",
    "重置统计": "Resetar Estatísticas",
    "导出数据": "Exportar Dados",
    "导入数据": "Importar Dados",
    "确定要重置所有统计数据吗？此操作不可撤销。": "Tem certeza que deseja resetar todas as estatísticas? Esta ação não pode ser desfeita.",
    # Windsurf Login page
    "Windsurf 登录取号": "Login Windsurf / Obter Token",
    "使用 Windsurf 账号密码登录，自动获取 API Key 并加入池": "Faça login com email e senha do Windsurf para obter a API Key e adicionar ao pool",
    "邮箱": "Email",
    "密码": "Senha",
    "使用代理": "Usar Proxy",
    "代理地址": "Endereço do Proxy",
    "登录并获取 API Key": "Login e Obter API Key",
    "登录中...": "Entrando...",
    "正在通过 Firebase 认证并获取 API Key...": "Autenticando via Firebase e obtendo API Key...",
    "Token 直接添加": "Adicionar Token Diretamente",
    "如果已有 auth token 或 API Key，直接粘贴即可添加到账号池": "Se já tem um auth token ou API Key, cole diretamente para adicionar ao pool",
    "粘贴 Token 或 API Key": "Cole o Token ou API Key",
    "添加到池": "Adicionar ao Pool",
    "可选标签": "Rótulo (opcional)",
    # Accounts page
    "账号管理": "Gerenciamento de Contas",
    "管理账号池中的所有账号及其状态": "Gerencie todas as contas do pool e seus status",
    "添加账号": "Adicionar Conta",
    "探测全部": "Sondar Todas",
    "刷新额度": "Atualizar Créditos",
    "ID": "ID",
    "标签": "Rótulo",
    "方式": "Método",
    "状态": "Status",
    "层级": "Nível",
    "额度": "Créditos",
    "用量": "Uso",
    "错误数": "Erros",
    "最后使用": "Último Uso",
    "操作": "Ações",
    "暂无账号": "Nenhuma conta",
    "启用": "Ativar",
    "停用": "Desativar",
    "探测": "Sondar",
    "删除": "Excluir",
    "重置错误": "Resetar Erros",
    "确定删除该账号吗？": "Tem certeza que deseja excluir esta conta?",
    "确定要删除账号": "Tem certeza que deseja excluir a conta",
    "删除后无法恢复": "Após excluir, não é possível recuperar",
    # Models page
    "模型控制": "Controle de Modelos",
    "查看和管理可用模型列表": "Visualize e gerencie a lista de modelos disponíveis",
    "模型列表": "Lista de Modelos",
    "可用模型": "Modelos Disponíveis",
    "刷新云端目录": "Atualizar Catálogo da Nuvem",
    "模型访问控制": "Controle de Acesso a Modelos",
    "全部放行": "Permitir Todos",
    "白名单": "Lista Branca",
    "黑名单": "Lista Negra",
    "仅允许以下模型": "Permitir apenas os seguintes modelos",
    "屏蔽以下模型": "Bloquear os seguintes modelos",
    "不限制模型访问": "Sem restrição de acesso a modelos",
    # Proxy page
    "代理配置": "Configuração de Proxy",
    "配置全局和每账号出口代理": "Configure proxy global e por conta",
    "全局代理": "Proxy Global",
    "设置全局出口代理，所有未配置独立代理的账号将使用此代理": "Defina o proxy global. Todas as contas sem proxy próprio usarão este",
    "主机": "Host",
    "端口": "Porta",
    "用户名": "Usuário",
    "保存": "Salvar",
    "移除": "Remover",
    "已保存": "Salvo",
    "已移除": "Removido",
    # Logs page
    "运行日志": "Logs de Execução",
    "通过 SSE 实时流式接收服务端日志": "Receba logs do servidor em tempo real via SSE",
    "级别": "Nível",
    "全部": "Todos",
    "搜索日志...": "Buscar nos logs...",
    "清空": "Limpar",
    "自动滚动": "Auto-scroll",
    "时间": "Hora",
    "消息": "Mensagem",
    # Experimental page
    "实验性功能": "Recursos Experimentais",
    "以下功能仍在测试阶段，可能不稳定": "Os recursos abaixo estão em fase de teste e podem ser instáveis",
    "Cascade 会话复用": "Reutilização de Sessão Cascade",
    "对话池": "Pool de Conversas",
    "条": "itens",
    "清空对话池": "Limpar Pool de Conversas",
    # Bans page
    "异常监测": "Monitoramento de Anomalias",
    "检测被限流或被封禁的账号": "Detecte contas limitadas ou banidas",
    "异常账号": "Contas com Anomalia",
    "已停用": "Desativadas",
    "自动错误停用": "Desativação por erro automático",
    "限流中": "Limitadas",
    "暂时不参与调度": "Temporariamente fora do pool",
    "重新启用": "Reativar",
    # Login overlay
    "WindsurfPool 控制台": "WindsurfPool - Painel",
    "输入密码以访问控制台": "Digite a senha para acessar",
    # Misc
    "未知": "Desconhecido",
    "无": "Nenhum",
    "确认": "Confirmar",
    "取消": "Cancelar",
    "关闭": "Fechar",
    "共": "Total:",
    "个账号": "contas",
    "加载中...": "Carregando...",
    "操作成功": "Operação realizada com sucesso",
    "操作失败": "Operação falhou",
    "复制成功": "Copiado com sucesso",
    "复制失败": "Falha ao copiar",
    "API Key 已复制": "API Key copiada",
    "请手动选择": "selecione manualmente",
    "已复制": "Copiado",
    # Browser auto-translate oddities
    "Faça login para obter um número.": "Login / Obter Token",
    "Gestão de contas": "Gerenciamento de Contas",
    "Monitoramento de anomalias": "Monitoramento de Anomalias",
    "Chaves de API": "Chaves de API",
    "Controle do modelo": "Controle de Modelos",
    "Configuração de proxy": "Configuração de Proxy",
    "Registro de execução": "Logs de Execução",
    "funções experimentais": "Recursos Experimentais",
    "Análise estatística": "Estatísticas",
    "Painel": "Painel",
}

with open(INPUT, 'r', encoding='utf-8') as f:
    content = f.read()

count = 0
for cn, pt in translations.items():
    if cn in content:
        content = content.replace(cn, pt)
        count += 1

# Also fix the HTML lang
content = content.replace('lang="zh-CN"', 'lang="pt-BR"')

with open(INPUT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Traduzido {count} strings de chinês para PT-BR")
