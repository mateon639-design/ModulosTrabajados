# Configuración de correo para alertas automáticas

Para que los módulos `retain_call_history` y `monitoreo_agente` puedan enviar alertas por correo electrónico, es necesario configurar el servidor de correo saliente (SMTP) en Odoo.

## Pasos para configurar el servidor de correo saliente

1. Ve a **Ajustes > Técnico > Correo > Servidores de correo saliente**.
2. Haz clic en **Nuevo** y completa los datos de tu proveedor SMTP (Gmail, Outlook, corporativo, etc.):
   - **Nombre**: Identificación del servidor (ejemplo: Alerta llamadas)
   - **SMTP Server**: Dirección del servidor SMTP (ejemplo: smtp.gmail.com)
   - **SMTP Port**: Puerto (ejemplo: 587 para Gmail)
   - **Username**: Correo electrónico que enviará las alertas
   - **Password**: Contraseña o app password del correo
   - **Connection Encryption**: TLS/STARTTLS recomendado
   - **FROM Filtering**: (Opcional) Nombre y correo que aparecerán como remitente
3. Haz clic en **Test Connection** para verificar la configuración.
4. Guarda los cambios.

## Notas importantes
- Sin esta configuración, Odoo no podrá enviar correos de alerta desde los módulos.
- Si usas Gmail, es recomendable crear una contraseña de aplicación y cambiar el nombre en la cuenta de Google si quieres personalizar el remitente.
- Puedes agregar varios destinatarios en el código, separados por coma.

## Ejemplo de configuración para Gmail
- SMTP Server: smtp.gmail.com
- SMTP Port: 587
- Username: tu_correo@gmail.com -agentegentatiana@gmail.com
- Password: contraseña de aplicación - piec krtw eajx tpae
- Connection Encryption: TLS (STARTTLS)

## Recomendación
Incluye esta configuración en la documentación para cualquier usuario que instale los módulos, y verifica que el servidor de correo esté activo y funcional antes de usar las alertas automáticas.
