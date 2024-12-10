# pylint: disable=invalid-name
"""
Helper for performance tests.
"""
import logging
import re
import sys

from pathlib import Path
from subprocess import Popen, PIPE
from typing import List, Tuple, Pattern, Any

from util.proc_io import ProcIO # type: ignore[import-untyped]


ON_POSIX = 'posix' in sys.builtin_module_names


class TimeoutException(Exception):
    """ Command timeout. """


class ImageRunFailed(Exception):
    """ Login to VM failed. """


class Performance:
    """
    Implementation of performance test.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(
        self,
        cycles=10
    ):
        logging.basicConfig(level=logging.DEBUG)
        self.image = None
        self.run_cmd = None
        self.cycles = cycles
        self.measurement_points = []

    def set_image(self, image: str):
        """ Set the image to test. """
        self.image = image

    def set_measurement_points(self, measurement_points: list[str]):
        """ Set measurement points. """
        measurement_pairs: List[Tuple[str, Pattern[Any]]] = []

        for i in range(0, len(measurement_points), 2):
            name = measurement_points[i]
            search = measurement_points[i+1]
            measurement_pairs.append((name, re.compile(search)))

        self.measurement_points = measurement_pairs

        logging.info('Measurement points:\n%s', self.measurement_points)

    def run_test(
        self,
        file: str = 'performance_report.txt',
        run_cmd = 'task run_performance_test'
    ) -> None:
        """ Run the performance test. """
        self.run_cmd = run_cmd

        points: List[List[Tuple[float, float, str, str]]] = []

        for i in range(0, self.cycles):
            logging.info('Executing performance run %d.', i)
            log = self._execute_test_run()
            points.append(self._evaluate_log(log))

        self._generate_report(points, file)

    def _generate_report(
        self,
        run_points: List[List[Tuple[float, float, str, str]]],
        file: str
    ) -> None:
        """ Generate performance test report. """
        results: dict[str, list[float]] = {}

        for run in run_points:
            for (delta, _ts, name, _log) in run:
                if name not in results:
                    results[name] = []
                results[name].append(delta)

        report_vals: List[Tuple[str, float, List[float]]] = []
        for (name, deltas) in results.items():
            avg = sum(deltas) / len(deltas)
            report_vals.append((name, avg, deltas))

        report_vals.sort(key=lambda l: l[1])

        report = f'Performance report:\n\nImage: {self.image}\n'
        report += f'Runs: {self.cycles}\n\nResults:\nms       name: test run results\n'
        for (name, avg, deltas) in report_vals:
            ds = ', '.join([f'{d:.6f}' for d in deltas])
            report += f'{avg:.6f} {name}: {ds}\n'

        logging.info('%s', report)

        with open(file, mode='w', encoding='utf-8') as f:
            f.write(report)

    def _evaluate_log(
        self,
        log: List[Tuple[str, str, float]]
    ) -> List[Tuple[float, float, str, str]]:
        """ Evaluate log of image run. """
        for (line, _, ts) in log:
            logging.info('%.6f %s', ts, line)

        point_logs = []
        for (name, regexp) in self.measurement_points:
            for (line, _, ts) in log:
                if regexp.search(line):
                    point_logs.append((ts, name, line.strip()))
                    continue

        point_logs.sort(key=lambda entry: entry[0])

        if not point_logs:
            logging.error('No measurement points found for run!')
            return []

        if len(point_logs) < len (self.measurement_points):
            logging.warning('No all measurement points found!')
        if len(point_logs) > len (self.measurement_points):
            logging.warning('Measurement points are not unique!')

        points: List[Tuple[float, float, str, str]] = []

        offset = point_logs[0][0]
        for (ts, name, line) in point_logs:
            delta = ts - offset
            points.append((delta, ts, name, line))

        logging.info('Measurement points: %s', str(points))

        eval_report = ''
        for point in points:
            eval_report += f'{point[0]}\t{point[2]}\t{point[1]}\t{point[3]}\n'

        logging.info('Test run evaluation:\n%s', eval_report)

        return points

    def _execute_test_run(self, timeout: int = 600) -> List[Tuple[str, str, float]]:
        """
        Execute the image.
        
        The assumption for a performance test image is that it will shutdown automatically.
        """
        if not self.image:
            logging.error('Performance: No image!')
            raise ImageRunFailed()

        path = Path(self.image)
        cwd = path.parent.parent.absolute()

        # open shell
        proc = Popen('bash', stdout=PIPE, stderr=PIPE, stdin=PIPE,
                     bufsize=1, close_fds=ON_POSIX, shell=True, encoding='utf-8',
                     cwd=cwd)
        # open IO threads for log timestamps
        pio = ProcIO(process=proc)
        pio.connect()

        # Run image and exit bash
        pio.write(f'{self.run_cmd}; exit\n')

        # Wait for image run to complete
        rc = proc.wait(timeout=timeout)
        # Check that run was OK
        if rc != 0:
            logging.error('Performance: Return code was %d!', rc)
            raise ImageRunFailed()

        # Collect all logs
        logs = []
        while pio.queue.qsize() > 0:
            logs.append(pio.queue.get())

        return logs
