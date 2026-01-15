// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载所有记录
    loadRecords();

    // 绑定提交按钮点击事件
    document.getElementById('submit-btn').addEventListener('click', addRecord);
});

// 添加收支记录
function addRecord() {
    // 获取表单数据
    const recordType = document.getElementById('record-type').value;
    const amount = document.getElementById('amount').value;
    const description = document.getElementById('description').value;

    // 简单校验
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
        alert('请输入有效的金额！');
        return;
    }

    // 发送POST请求到后端
    fetch('/add_record', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: recordType,
            amount: amount,
            description: description
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.msg);
        if (data.code === 200) {
            // 清空表单
            document.getElementById('amount').value = '';
            document.getElementById('description').value = '';
            // 重新加载记录
            loadRecords();
        }
    })
    .catch(error => {
        console.error('添加失败：', error);
        alert('网络错误，请重试！');
    });
}

// 加载所有收支记录
function loadRecords() {
    // 发送GET请求到后端
    fetch('/get_records')
    .then(response => response.json())
    .then(data => {
        if (data.code === 200) {
            // 更新统计数据
            document.getElementById('total-income').textContent = data.summary.income.toFixed(2);
            document.getElementById('total-expense').textContent = data.summary.expense.toFixed(2);
            document.getElementById('balance').textContent = data.summary.balance.toFixed(2);

            // 更新记录列表
            const recordsList = document.getElementById('records-list');
            recordsList.innerHTML = '';

            if (data.data.length === 0) {
                recordsList.innerHTML = '<tr class="empty-tip"><td colspan="4">暂无收支记录</td></tr>';
                return;
            }

            // 遍历记录生成表格行
            data.data.forEach(record => {
                const tr = document.createElement('tr');
                // 格式化时间
                const time = new Date(record.create_time).toLocaleString('zh-CN');
                tr.innerHTML = `
                    <td>${time}</td>
                    <td>${record.type}</td>
                    <td>${parseFloat(record.amount).toFixed(2)}</td>
                    <td>${record.description || '-'}</td>
                `;
                recordsList.appendChild(tr);
            });
        } else {
            alert(data.msg);
        }
    })
    .catch(error => {
        console.error('查询失败：', error);
        alert('网络错误，请重试！');
    });
}