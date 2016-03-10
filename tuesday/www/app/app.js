var app = angular.module('pasp', ['ngRoute', 'ui.bootstrap']);

app.config(function ($locationProvider, $routeProvider) {
    $locationProvider.html5Mode(true).hashPrefix('!');

    return $routeProvider.when('/', {
        templateUrl: 'app/main/home.html',
        controller: 'HomeController'
    })
   .when('/rank', {
       redirectTo: '/'
   })
   .when('/rank/:words/', {
       templateUrl: 'app/main/rank.html',
       controller: 'RankController'
   })
   .when('/document/:doc_id', {
       templateUrl: 'app/main/document.html',
       controller: 'DocumentController'
   })
   .when('/document/:doc_id/keywords', {
       templateUrl: 'app/main/keywords.html',
       controller: 'KeywordController'
   })
   .when('/document/:doc_id/corpus/:corpus_id/keywords', {
       templateUrl: 'app/main/keywords.html',
       controller: 'KeywordController'
   })
   .when('/corpus/:corpus_id/keywords', {
       templateUrl: 'app/main/keywords.html',
       controller: 'KeywordController'
   })
   .otherwise({
       templateUrl: 'app/main/rawApi.html',
       controller: 'RawApiController'
   });
});

// There is already a limitTo filter built-into angular,
// Here is a startFrom filter
// Credit to: http://stackoverflow.com/users/1397051/andy-joslin
app.filter('startFrom', function () {
    return function (input, start) {
        start = +start; //parse to int
        return input.slice(start);
    }
});

app.controller('HomeController', function ($scope, $http, $location) {
    $scope.apiUrl = 'http://' + $location.host() + ':' + $location.port() + '/api/v1/rank'
    $scope.text = $location.path().replace('/', ' ')

    $scope.data = []

    $http.get($scope.apiUrl)
        .success(function (data) { $scope.data = data })
        .error(function (fail) { });
});

