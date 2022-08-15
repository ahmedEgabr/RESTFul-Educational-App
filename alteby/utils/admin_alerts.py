from django.utils.safestring import mark_safe

def render_alert(message, error=False, warning=False, alert=False, tag="small", color=None):
    if error and alert:
        classes = "alert-danger"
    elif warning and alert:
        classes = "alert-warning"
    elif error and tag:
        classes = "text-danger"
    elif warning and tag:
        classes = "text-warning"
    
    if alert:
        html_body = f'''
        <div class="alert {classes} alert-dismissible">
            <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
            <i class="icon fa fa-ban"></i>{message}
        </div>
        '''
    elif tag:
        if color:
            html_body = f'<{tag} style="color:{color}">{message}</{tag}>'
        else:
            html_body = f'<{tag} class="{classes}">{message}</{tag}>'
    return mark_safe(html_body)
    