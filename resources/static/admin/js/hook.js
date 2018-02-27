jQuery(function () {
    hook_backup();
    hook_strategy();
    hook_account();
    $.ajaxSetup({
        headers: {'X-CSRFToken': $.cookie('uams_csrftoken')}
    });
});
function lock(uid, username) {
    if (confirm('确定要冻结"'+username+'"？')) {
        $.post( "/backend/lock", {uid:uid}, function( data ) {
            location.reload();
        });
    }
}

function unlock(uid, username) {
    if (confirm('确定要解冻"'+username+'"？')) {
        $.post( "/backend/unlock", {uid:uid}, function( data ) {
            location.reload();
        });
    }
}
function hook_strategy() {
    if(location.href.indexOf('backup/strategy')>0){
        $.post("/backup/count_valid_strategy", function( data ) {
            if(data.error || data.data>0)
                return;
            $("#changelist > .toolbar-content").
            prepend('<div class="alert alert-block alert-warn">注意：当前未启用任何备份策略，无法执行自动备份</div>');
        });

    }

}
function recovery(bid) {
    if (confirm('确定要还原账号数据？')) {
        $.post("/backup/recovery", {bid: bid}, function( data ) {
            if(data.error)
                alert(data.error);
            else{
                mask(true, '数据还原中，请稍等...');
                checkFinished();
            }
        });
    }
}
function mask(show, msg) {
    if(show){
        $("#mask_msg").text(msg);
        $('#mask_modal').modal({
            backdrop: 'static',
            keyboard: false
        });
    }else{
        $("#mask_msg").text('');
        $('#mask_modal').modal('hide');
    }
}
var checkFinishedInterval;
function checkFinished() {
    checkFinishedInterval = setInterval(function () {
        $.post( "/backup/recovery_check", function( data ) {
            clearInterval(checkFinishedInterval);
            if(data.error)
                alert(data.error);
            else{
                mask(false);
                alert('还原成功')
            }
        });
    },2000);
}
function hook_backup() {
    if(location.href.indexOf('backup/backup')>0){
        $("#changelist > .toolbar-content").hide();
        $(".field-date").each(function () {
            this.innerHTML = this.innerText;
        })
        var modal ='\
            <div class="modal fade" id="mask_modal" tabindex="-1" role="dialog" aria-labelledby="mask_msg" data-backdrop="static" data-keyboard="false" aria-hidden="true">\
            <div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header">\
            <h5 class="modal-title" id="mask_msg">--MSG--</h5></div></div></div></div>';
        $('body').append(modal);
    }

}

function hook_account() {
    if(location.href.indexOf('/account/account')>0&&location.href.indexOf('/change/')>0){
        $(".field-site").hide();
    }

}