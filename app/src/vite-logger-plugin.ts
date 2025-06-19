export function runtimeLogger() {
  return {
    name: 'runtime-logger',
    configureServer(server) {
      server.httpServer?.once('listening', () => {
        console.log('Vite dev server started');
      });
    }
  };
}

export function preTransformLogger(logger: any, logFile: string) {
  return logger;
}
