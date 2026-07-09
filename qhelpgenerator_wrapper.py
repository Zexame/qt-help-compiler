import os
import subprocess
import logging


class QHelpGeneratorWrapper:
    """Запуск qhelpgenerator."""

    def __init__(self, qhelp_path):
        self.qhelp_path = qhelp_path

    def generate(self, qhp_path, qhcp_path, output_path, verbose=False):
        logging.info(f"Запуск qhelpgenerator: {self.qhelp_path}")

        cmd = [self.qhelp_path, qhp_path, "-o", output_path]

        if qhcp_path and os.path.exists(qhcp_path):
            cmd = [self.qhelp_path, qhcp_path, "-o", output_path]
            logging.debug("Используется .qhcp")
        else:
            logging.warning(".qhcp не найден, используется только .qhp")

        try:
            if verbose:
                result = subprocess.run(cmd, capture_output=False, text=True, check=False)
                success = result.returncode == 0
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                success = result.returncode == 0
                if not success:
                    logging.error(f"Код возврата: {result.returncode}")
                    if result.stderr:
                        logging.error(f"stderr: {result.stderr}")
                    if result.stdout:
                        logging.error(f"stdout: {result.stdout}")

            if success:
                logging.info("qhelpgenerator завершил работу")
            else:
                logging.error(f"Ошибка (код: {result.returncode})")
            return success

        except FileNotFoundError:
            logging.error(f"qhelpgenerator не найден: {self.qhelp_path}")
            return False
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            return False