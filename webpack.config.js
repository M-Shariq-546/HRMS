const path = require('path');

module.exports = {
  entry: './static/src/js/integrations/IntegrationsApp.jsx',
  output: {
    path: path.resolve(__dirname, 'static/dist/js'),
    filename: 'integrations-app.js',
    publicPath: '/static/dist/js/'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'static'),
    },
    compress: true,
    port: 3000,
    hot: true
  }
}; 