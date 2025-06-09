#!/bin/bash

case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

PATH_TO_MANAGE_PY=$(find ../ -name "manage.py" -not -path "*/env" -not -path "*/venv");
BASE_DIR="$(dirname "${PATH_TO_MANAGE_PY}")";
cd $BASE_DIR
status=$?;
if [ $status -ne 0 ]; then
    echo "Убедитесь, что в проекте содержится только один файл manage.py";
    exit $status;
fi

echo "Очистка тестовых пользователей..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
     usernames_list = ['vasya.ivanov', 'second-user', 'third-user-username', 'NoEmail', 'NoFirstName', 'NoLastName', 'NoPassword', 'TooLongEmail', \
     'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-', \
     'TooLongFirstName', 'TooLongLastName', 'InvalidU\$ername', 'EmailInUse']; \
     deleted_count, _ = User.objects.filter(username__in=usernames_list).delete(); \
     print(f'Удалено {deleted_count} тестовых пользователей');" | $python manage.py shell

echo "База данных очищена от тестовых пользователей."
