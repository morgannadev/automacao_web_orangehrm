# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False


def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.FIREFOX

    # Uncomment to set the WebDriver path
    bot.driver_path = r"resources\geckodriver.exe" 

    # Contadores
    total_itens = 0
    itens_com_sucesso = 0
    itens_que_falharam = 0

    try:
        # Opens the BotCity website.
        bot.browse("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        login_orange(
            bot, 
            maestro.get_credential(label="login_orange", key="username"), 
            maestro.get_credential(label="login_orange", key="password")
        )

        datapool = maestro.get_datapool(label="orange_cadastro")
        while datapool.has_next():
            item = datapool.next(task_id=execution.task_id)

            if item is None:
                break

            total_itens += 1

            open_form(bot)

            candidato = fill_form(bot, item)

            if candidato:
                item.report_done()
                itens_com_sucesso += 1

                maestro.new_log_entry(
                    activity_label="cadastro_orange",
                    values={
                        "name": item.get_value("full_name"),
                        "message": "Cadastrado com sucesso."
                    }
                )
            else:
                item.report_error()
                itens_que_falharam += 1

                maestro.new_log_entry(
                    activity_label="cadastro_orange",
                    values={
                        "name": item.get_value("full_name"),
                        "message": "Cadastrado falhou."
                    }
                )

            if itens_que_falharam > 0:
                status = AutomationTaskFinishStatus.PARTIALLY_COMPLETED
                message = "Executou parcialmente"
            else:
                status = AutomationTaskFinishStatus.SUCCESS
                message = "Executou com sucesso"


    except Exception as error:
        status = AutomationTaskFinishStatus.FAILED
        message = "Execução falhou. " + str(error)

        bot.save_screenshot('error.png')

        maestro.error(
            task_id=execution.task_id,
            exception=error,
            screenshot="error.png"
        )
    
    finally:   
        bot.wait(3000)
        bot.stop_browser()

        maestro.finish_task(
            task_id=execution.task_id,
            status=status,
            message=message,
            total_items=total_itens,
            processed_items=itens_com_sucesso,
            failed_items=itens_que_falharam
        )


def not_found(label):
    print(f"Element not found: {label}")

def login_orange(bot: WebBot, username: str, password: str):
    username_label = bot.find_element(
        '/html/body/div/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/div/div[2]/input',
        By.XPATH
    )

    username_label.send_keys(username)

    password_label = bot.find_element(
        '/html/body/div/div[1]/div/div[1]/div/div[2]/div[2]/form/div[2]/div/div[2]/input',
        By.XPATH
    )
    password_label.send_keys(password)

    bot.enter()
    bot.wait(2000)

def open_form(bot: WebBot):
    bot.wait(3000)

    recruitment_button = bot.find_element(
        '/html/body/div/div[1]/div[1]/aside/nav/div[2]/ul/li[5]/a',
        By.XPATH
    )

    recruitment_button.click()

    bot.wait(3000)

    add_button = bot.find_element(
        '/html/body/div/div[1]/div[2]/div[2]/div/div[2]/div[1]/button',
        By.XPATH
    )

    add_button.click()

    bot.wait(3000)

def fill_form(bot: WebBot, item_candidato):
    try:
        name = item_candidato["full_name"]

        first_name = bot.find_element(
            '/html/body/div/div[1]/div[2]/div[2]/div/div/form/div[1]/div/div/div/div[2]/div[1]/div[2]/input',
            By.XPATH
        )

        first_name.send_keys(name.split(" ")[0])

        middle_name = bot.find_element(
            '/html/body/div/div[1]/div[2]/div[2]/div/div/form/div[1]/div/div/div/div[2]/div[2]/div[2]/input',
            By.XPATH
        )

        middle_name.send_keys(name.split(" ")[1])

        last_name = bot.find_element(
            '/html/body/div/div[1]/div[2]/div[2]/div/div/form/div[1]/div/div/div/div[2]/div[3]/div[2]/input',
            By.XPATH
        )

        last_name.send_keys(name.split(" ")[2:])

        bot.wait(1000)

        vacancy = bot.find_element(
            '.oxd-select-text',
            By.CSS_SELECTOR
        )

        vacancy.click()

        vacancy_options = bot.find_elements(
            'div.oxd-select-option > span:nth-child(1)',
            By.CSS_SELECTOR
        )

        for option in vacancy_options:
            if option.text == item_candidato["vacancy"]:
                option.click()
                bot.wait(1000)
                break

        email = bot.find_element(
            '/html/body/div/div[1]/div[2]/div[2]/div/div/form/div[3]/div/div[1]/div/div[2]/input',
            By.XPATH
        )

        email.send_keys(item_candidato["email"])

        contact_number = bot.find_element(
            '/html/body/div/div[1]/div[2]/div[2]/div/div/form/div[3]/div/div[2]/div/div[2]/input',
            By.XPATH
        )

        contact_number.send_keys(item_candidato["contact_number"])

        keywords = bot.find_element(
            '/html/body/div/div[1]/div[2]/div[2]/div/div/form/div[5]/div/div[1]/div/div[2]/input',
            By.XPATH
        )

        keywords.send_keys(item_candidato["keywords"])

        save_button = bot.find_element(
            '/html/body/div/div[1]/div[2]/div[2]/div/div/form/div[8]/button[2]',
            By.XPATH
        )

        save_button.click()

        bot.wait(2000)

        return True

    except Exception as error:
        return False

if __name__ == '__main__':
    main()
