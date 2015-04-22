manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

$manage syncdb --noinput --migrate
$manage collectstatic --noinput

sudo supervisorctl restart actionforwomen_mobi actionforwomen_mobi_celery
