$(document).ready(function() {
    var taskRunning = false;
    setInterval(function() {
        $.get("/api/task_status", function(d) {
            taskRunning = !!d.running;
        });
    }, 2000);
    setInterval(function() {
        var terminal = $("#log-terminal");
        if (terminal.length > 0 && taskRunning) {
            $.get("/api/logs", function(data) {
                if (data.logs && data.logs.length > 0) {
                    data.logs.forEach(function(log) {
                        terminal.append('<div class="log-line">' + log + '</div>');
                    });
                    if (terminal[0]) {
                        terminal.scrollTop(terminal[0].scrollHeight);
                    }
                }
            }).fail(function() {});
        }
    }, 3000);

    // 状态更新轮询
    setInterval(updateStats, 5000);

    // 绑定按钮事件
    $(".action-btn").click(function() {
        var action = $(this).data("action");
        var btn = $(this);
        var stopOnSuccess = $("#stopOnSuccess").is(":checked"); // 获取开关状态
        var showBrowser = $("#showBrowser").is(":checked"); // 获取显示浏览器开关状态
        var errorKeywords = $("#errorKeywords").val(); // 获取错误关键词
        
        btn.prop("disabled", true);
        
        $.post("/api/start_task/" + action, { 
            stop_on_success: stopOnSuccess,
            show_browser: showBrowser,
            error_keywords: errorKeywords
        }, function(resp) {
            alert(resp.message);
            btn.prop("disabled", false);
        }).fail(function() {
            alert("任务启动失败");
            btn.prop("disabled", false);
        });
    });
    
    $("#stop-btn").click(function() {
        if(confirm("确定要停止所有正在运行的任务吗？")) {
             $.post("/api/stop_task", function(resp) {
                alert(resp.message);
            });
        }
    });

    updateStats();
});

function updateStats() {
    // 仅当页面上有统计元素时才更新
    if ($("#count-total").length > 0) {
        $.get("/api/stats", function(data) {
            $("#count-total").text(data.total);
            $("#count-simple").text(data.simple);
            $("#count-complex").text(data.complex);
            $("#count-success").text(data.success);
        }).fail(function() {
            // 忽略错误
        });
    }
}
