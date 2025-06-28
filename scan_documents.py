#!/usr/bin/env python
"""
Скрипт для сканирования документов с помощью сканера
"""

import os
import sys
import django
from pathlib import Path
import logging
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archie.settings')
django.setup()

from archie.documents.models import Document
from archie.services.llm_service import LLMService
import tempfile

logger = logging.getLogger(__name__)


class DocumentScanner:
    """Класс для сканирования документов"""
    
    def __init__(self):
        """Инициализация сканера"""
        self.llm_service = LLMService()
        self.scan_directory = project_root / "scanned_documents"
        self.scan_directory.mkdir(exist_ok=True)
    
    def scan_document(self, scanner_name: str = None, resolution: int = 300) -> str:
        """
        Сканирует документ с помощью подключенного сканера
        
        Args:
            scanner_name: Имя сканера (если None, используется первый доступный)
            resolution: Разрешение сканирования в DPI
            
        Returns:
            Путь к отсканированному файлу
        """
        try:
            # Проверяем доступность сканера
            if not self._check_scanner_available():
                logger.error("Сканер не найден или недоступен")
                return None
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_{timestamp}.jpg"
            filepath = self.scan_directory / filename
            
            # Сканируем документ
            logger.info(f"Начинаем сканирование документа: {filename}")
            
            # Используем SANE для сканирования (Linux)
            if self._scan_with_sane(filepath, scanner_name, resolution):
                logger.info(f"Документ успешно отсканирован: {filepath}")
                return str(filepath)
            
            # Fallback: используем другие методы
            if self._scan_with_other_methods(filepath, scanner_name, resolution):
                logger.info(f"Документ успешно отсканирован: {filepath}")
                return str(filepath)
            
            logger.error("Не удалось отсканировать документ")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при сканировании: {e}")
            return None
    
    def _check_scanner_available(self) -> bool:
        """Проверяет доступность сканера"""
        try:
            # Проверяем SANE
            import subprocess
            result = subprocess.run(['scanimage', '--list-devices'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                logger.info("SANE сканеры найдены:")
                logger.info(result.stdout)
                return True
            
            # Проверяем другие методы
            logger.warning("SANE сканеры не найдены, проверяем альтернативы...")
            return self._check_alternative_scanners()
            
        except FileNotFoundError:
            logger.warning("SANE не установлен")
            return self._check_alternative_scanners()
        except Exception as e:
            logger.error(f"Ошибка при проверке сканера: {e}")
            return False
    
    def _check_alternative_scanners(self) -> bool:
        """Проверяет альтернативные методы сканирования"""
        try:
            # Проверяем Windows WIA
            import win32com.client
            wia = win32com.client.Dispatch('WIA.DeviceManager')
            devices = wia.DeviceInfos
            for device in devices:
                if device.Type == 1:  # Scanner device
                    logger.info(f"Найден WIA сканер: {device.Properties('Name').Value}")
                    return True
        except ImportError:
            logger.warning("pywin32 не установлен")
        except Exception as e:
            logger.warning(f"WIA недоступен: {e}")
        
        # Проверяем macOS Image Capture
        if sys.platform == "darwin":
            try:
                import subprocess
                result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                      capture_output=True, text=True)
                if "scanner" in result.stdout.lower():
                    logger.info("Найден macOS сканер")
                    return True
            except Exception as e:
                logger.warning(f"Не удалось проверить macOS сканеры: {e}")
        
        return False
    
    def _scan_with_sane(self, filepath: Path, scanner_name: str, resolution: int) -> bool:
        """Сканирует документ с помощью SANE"""
        try:
            import subprocess
            
            # Формируем команду сканирования
            cmd = [
                'scanimage',
                '--format=jpeg',
                f'--resolution={resolution}',
                f'--output-file={filepath}'
            ]
            
            if scanner_name:
                cmd.extend(['--device-name', scanner_name])
            
            logger.info(f"Выполняем команду: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and filepath.exists():
                return True
            else:
                logger.error(f"Ошибка SANE: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.warning("SANE не установлен")
            return False
        except Exception as e:
            logger.error(f"Ошибка при сканировании с SANE: {e}")
            return False
    
    def _scan_with_other_methods(self, filepath: Path, scanner_name: str, resolution: int) -> bool:
        """Сканирует документ альтернативными методами"""
        try:
            # Windows WIA
            if sys.platform == "win32":
                return self._scan_with_wia(filepath, scanner_name, resolution)
            
            # macOS Image Capture
            elif sys.platform == "darwin":
                return self._scan_with_image_capture(filepath, scanner_name, resolution)
            
            # Linux альтернативы
            else:
                return self._scan_with_linux_alternatives(filepath, scanner_name, resolution)
                
        except Exception as e:
            logger.error(f"Ошибка при альтернативном сканировании: {e}")
            return False
    
    def _scan_with_wia(self, filepath: Path, scanner_name: str, resolution: int) -> bool:
        """Сканирует документ с помощью Windows WIA"""
        try:
            import win32com.client
            
            wia = win32com.client.Dispatch('WIA.DeviceManager')
            devices = wia.DeviceInfos
            
            for device in devices:
                if device.Type == 1:  # Scanner device
                    if not scanner_name or device.Properties('Name').Value == scanner_name:
                        scanner = device.Connect()
                        item = scanner.Items[1]  # First item
                        
                        # Настраиваем параметры сканирования
                        item.Properties('Horizontal Resolution').Value = resolution
                        item.Properties('Vertical Resolution').Value = resolution
                        item.Properties('Horizontal Extent').Value = 2480  # A4 width
                        item.Properties('Vertical Extent').Value = 3508   # A4 height
                        
                        # Сканируем
                        image = item.Transfer()
                        image.SaveFile(str(filepath))
                        return True
            
            return False
            
        except ImportError:
            logger.warning("pywin32 не установлен")
            return False
        except Exception as e:
            logger.error(f"Ошибка WIA сканирования: {e}")
            return False
    
    def _scan_with_image_capture(self, filepath: Path, scanner_name: str, resolution: int) -> bool:
        """Сканирует документ с помощью macOS Image Capture"""
        try:
            import subprocess
            
            # Используем sips для сканирования
            cmd = [
                'sips',
                '-s', 'format', 'jpeg',
                '--out', str(filepath),
                '--resampleHeightWidth', str(resolution), str(resolution)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and filepath.exists()
            
        except Exception as e:
            logger.error(f"Ошибка Image Capture сканирования: {e}")
            return False
    
    def _scan_with_linux_alternatives(self, filepath: Path, scanner_name: str, resolution: int) -> bool:
        """Сканирует документ альтернативными Linux методами"""
        try:
            # Пробуем xsane
            import subprocess
            cmd = ['xsane', '--save', str(filepath)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and filepath.exists():
                return True
            
            # Пробуем gscan2pdf
            cmd = ['gscan2pdf', '--output', str(filepath)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and filepath.exists():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка Linux альтернативного сканирования: {e}")
            return False
    
    def process_scanned_document(self, filepath: str, title: str = None, category: str = None) -> Document:
        """
        Обрабатывает отсканированный документ и создает запись в базе данных
        
        Args:
            filepath: Путь к отсканированному файлу
            title: Название документа (если None, генерируется автоматически)
            category: Категория документа (если None, генерируется автоматически)
            
        Returns:
            Созданный объект Document
        """
        try:
            # Анализируем документ с помощью LLM
            analysis_result = self.llm_service.analyze_document(filepath)
            
            # Создаем документ
            document = Document(
                title=title or analysis_result.get('title', 'Отсканированный документ'),
                category=category or analysis_result.get('category', 'Документы'),
                text=analysis_result.get('description', 'Документ отсканирован в системе Archie'),
                scan=filepath
            )
            document.save()
            
            logger.info(f"Документ создан: {document.title}")
            return document
            
        except Exception as e:
            logger.error(f"Ошибка при обработке отсканированного документа: {e}")
            return None


def main():
    """Основная функция для сканирования документов"""
    print("🖨️  Archie Document Scanner")
    print("=" * 40)
    
    scanner = DocumentScanner()
    
    # Проверяем доступность сканера
    if not scanner._check_scanner_available():
        print("❌ Сканер не найден или недоступен")
        print("\nУстановите один из следующих пакетов:")
        print("- Linux: sudo apt-get install sane-utils xsane")
        print("- Windows: pip install pywin32")
        print("- macOS: используйте встроенный Image Capture")
        return
    
    print("✅ Сканер найден и готов к работе")
    
    # Сканируем документ
    print("\n📄 Начинаем сканирование...")
    scanned_file = scanner.scan_document()
    
    if scanned_file:
        print(f"✅ Документ отсканирован: {scanned_file}")
        
        # Обрабатываем документ
        print("\n🤖 Обрабатываем документ с помощью ИИ...")
        document = scanner.process_scanned_document(scanned_file)
        
        if document:
            print(f"✅ Документ сохранен в базе данных:")
            print(f"   📝 Название: {document.title}")
            print(f"   🏷️  Категория: {document.category}")
            print(f"   📋 Описание: {document.text}")
        else:
            print("❌ Ошибка при сохранении документа")
    else:
        print("❌ Ошибка при сканировании")


if __name__ == "__main__":
    main() 