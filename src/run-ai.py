#!/usr/bin/env python3
import multiprocessing

from ai_service.server import start_app

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    start_app()
